import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from backend.core.cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://notams.aim.faa.gov"
SEARCH_PATH = "/notamSearch/"
SEARCH_URL = f"{BASE_URL}{SEARCH_PATH}search"
APP_URL = f"{BASE_URL}{SEARCH_PATH}nsapp.html"
RESULTS_URL = f"{APP_URL}#/results"

class NotamServiceError(Exception):
    """Custom exception for NOTAM service errors."""
    pass

class NotamSession:
    """Manages a session with the NOTAM search service."""
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # retry on these HTTP status codes
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set up browser-like headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": BASE_URL,
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })
        
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the session by getting necessary cookies."""
        if self._initialized:
            return True

        try:
            # Step 1: Load the main NOTAM search page
            response = self.session.get(f"{BASE_URL}/notamSearch/")
            response.raise_for_status()
            logger.info(f"Initial request status code: {response.status_code}")
            logger.info(f"Initial cookies: {[cookie.name for cookie in self.session.cookies]}")

            # Add referer header for subsequent requests
            self.session.headers.update({
                "Referer": f"{BASE_URL}/notamSearch/"
            })

            # Step 2: Initialize session with disclaimer acceptance
            session_url = f"{BASE_URL}/notamSearch/session"
            response = self.session.post(
                session_url,
                data="agreed=true",  # Exactly as seen in browser
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Content-Length": "11"  # Length of "agreed=true"
                }
            )
            response.raise_for_status()
            logger.info(f"Session initialization status code: {response.status_code}")

            # Check if we got the JSESSIONID cookie
            cookies = self.session.cookies
            logger.info(f"Current cookies: {[cookie.name for cookie in cookies]}")
            
            if 'JSESSIONID' not in cookies:
                error_msg = "Failed to obtain JSESSIONID cookie"
                logger.error(error_msg)
                raise NotamServiceError(error_msg)

            # Log all cookies for debugging
            logger.info("Final cookies received:")
            for cookie in cookies:
                logger.info(f"Cookie: {cookie.name} = {cookie.value[:10]}... (Domain: {cookie.domain}, Path: {cookie.path})")

            self._initialized = True
            logger.info("NotamSession initialized successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to initialize NOTAM session: {str(e)}")
            raise NotamServiceError(f"Session initialization failed: {str(e)}")

    def is_initialized(self) -> bool:
        """Check if the session has been properly initialized."""
        return self._initialized
    
def _parse_notam_date(date_str: Optional[str]) -> Optional[str]:
    """Safely parses NOTAM date string, handling 'PERM' and other edge cases."""
    if not date_str:
        return None
    
    # Clean the string (e.g., "10/20/2025 1200 EST")
    cleaned_str = date_str.split('EST')[0].strip()
    
    if cleaned_str == "PERM":
        return None  # A permanent NOTAM has no end date, so None is appropriate

    try:
        return datetime.strptime(cleaned_str, "%m/%d/%Y %H%M").isoformat()
    except ValueError:
        # Log the error but continue
        logger.warning(f"Could not parse NOTAM date string: {date_str}")
        return None
    
# Create a global session instance
_notam_session = NotamSession()

def get_notams(icao_code: str) -> List[Dict[str, Any]]:
    """
    Fetches NOTAMs for a given ICAO code by scraping the FAA NOTAM Search website.

    Args:
        icao_code: The ICAO code of the airport.

    Returns:
        A list of dictionaries, where each dictionary contains NOTAM details.
        Each dictionary includes 'number', 'type', 'issued', 'text' fields.
        Returns an empty list if no NOTAMs are found or if the request fails.
    """
    cache_key = f"notams_{icao_code}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        if not _notam_session.is_initialized():
            _notam_session.initialize()

        # Step 1: Load the SPA page
        response = _notam_session.session.get(APP_URL)
        response.raise_for_status()
        logger.info("Loaded SPA page")

        # Step 2: Make the search request with all required parameters
        payload = {
            'searchType': '0',
            'designatorsForLocation': icao_code,
            'designatorForAccountable': '',
            'latDegrees': '',
            'latMinutes': '0',
            'latSeconds': '0',
            'longDegrees': '',
            'longMinutes': '0',
            'longSeconds': '0',
            'radius': '10',
            'sortColumns': '5 false',
            'sortDirection': 'true',
            'designatorForNotamNumberSearch': '',
            'notamNumber': '',
            'radiusSearchOnDesignator': 'false',
            'radiusSearchDesignator': '',
            'latitudeDirection': 'N',
            'longitudeDirection': 'W',
            'freeFormText': '',
            'flightPathText': '',
            'flightPathDivertAirfields': '',
            'flightPathBuffer': '4',
            'flightPathIncludeNavaids': 'true',
            'flightPathIncludeArtcc': 'false',
            'flightPathIncludeTfr': 'true',
            'flightPathIncludeRegulatory': 'false',
            'flightPathResultsType': 'All NOTAMs',
            'archiveDate': '',
            'archiveDesignator': '',
            'offset': '0',
            'notamsOnly': 'false',
            'filters': '',
            'minRunwayLength': '',
            'minRunwayWidth': '',
            'runwaySurfaceTypes': '',
            'predefinedAbraka': '',
            'predefinedDabra': '',
            'flightPathAddlBuffer': ''
        }

        # Update headers for the search request
        _notam_session.session.headers.update({
            "Referer": RESULTS_URL,
            "Priority": "u=1, i"
        })

        # Make the POST request to get NOTAMs
        response = _notam_session.session.post(SEARCH_URL, data=payload)
        response.raise_for_status()
        
        logger.info(f"Search response status: {response.status_code}")
        
        # Parse JSON response
        data = response.json()
        logger.info(f"Found {data.get('totalNotamCount', 0)} total NOTAMs")
        
        result = []
        for notam in data.get('notamList', []):
            # Convert dates to standardized format
            issue_date = _parse_notam_date(notam.get('issueDate'))
            start_date = _parse_notam_date(notam.get('startDate'))
            end_date = _parse_notam_date(notam.get('endDate'))
            
            notam_data = {
                'number': notam.get('notamNumber', ''),
                'type': notam.get('featureName', ''),
                'issued': issue_date,
                'start_date': start_date,
                'end_date': end_date,
                'status': notam.get('status', ''),
                'icao_message': notam.get('icaoMessage', ''),
                'traditional_message': notam.get('traditionalMessage', ''),
                'plain_language_message': notam.get('plainLanguageMessage', ''),
                'facility': notam.get('facilityDesignator', ''),
                'icao_id': notam.get('icaoId', ''),
                'airport_name': notam.get('airportName', ''),
                'keyword': notam.get('keyword', ''),
                'cancelled_or_expired': notam.get('cancelledOrExpired', False)
            }
            result.append(notam_data)

        # Cache the results for 15 minutes (NOTAMs update frequently)
        cache.set(cache_key, result, ttl_seconds=900)
        return result

    except requests.RequestException as e:
        logger.error(f"Error fetching NOTAMs for {icao_code}: {e}")
        raise NotamServiceError(f"Failed to retrieve NOTAMs: {e}")
    except Exception as e:
        logger.error(f"Error parsing NOTAMs for {icao_code}: {e}")
        raise NotamServiceError(f"Failed to parse NOTAMs: {e}")

if __name__ == "__main__":
    print("--- Testing NOTAM Service ---")
    try:
        notams = get_notams("KSFO")
        print(f"Found {len(notams)} NOTAMs for KSFO")
        for notam in notams:
            print("\n" + "="*50)
            print(f"NOTAM {notam['number']} - {notam['type']}")
            #print(f"Status: {notam['status']}")
            #print(f"Issued: {notam['issued']}")
            #print(f"Start Date: {notam['start_date']}")
            #print(f"End Date: {notam['end_date']}")
            #print(f"Facility: {notam['facility']} ({notam['airport_name']})")
            #print(f"Keyword: {notam['keyword']}")
            #print("\nTraditional Message:")
            #print(notam['traditional_message'])
            #print("\nICAO Message:")
            #print(notam['icao_message'])
    except NotamServiceError as e:
        print(f"Caught NOTAM Service Error: {e}")
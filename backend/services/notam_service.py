import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
from backend.core.cache import cache

NOTAM_URL = "https://notams.aim.faa.gov/notamSearch/nsapp.html#/results"

class NotamServiceError(Exception):
    """Custom exception for NOTAM service errors."""
    pass

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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # First request to get the session cookie
        session = requests.Session()
        session.get(NOTAM_URL, headers=headers)

        # Construct the search payload
        payload = {
            'designatorsForLocation': icao_code,
            'radiusForLocation': '',
            'listOption': '0',  # Current NOTAMs
            'orderOption': '1',  # Order by location
            'searchType': '0',   # Search by location
            'formatType': '0'    # Domestic format
        }

        # Make the POST request to get NOTAMs
        response = session.post(NOTAM_URL, headers=headers, data=payload)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        notam_elements = soup.find_all('div', class_='notam-results')
        
        result = []
        for element in notam_elements:
            notam_data = {
                'number': element.find('div', class_='notam-number').text.strip() if element.find('div', class_='notam-number') else '',
                'type': element.find('div', class_='notam-type').text.strip() if element.find('div', class_='notam-type') else '',
                'issued': element.find('div', class_='notam-issued').text.strip() if element.find('div', class_='notam-issued') else '',
                'text': element.find('div', class_='notam-text').text.strip() if element.find('div', class_='notam-text') else ''
            }
            result.append(notam_data)

        # Cache the results for 15 minutes (NOTAMs update frequently)
        cache.set(cache_key, result, ttl_seconds=900)
        return result

    except requests.RequestException as e:
        print(f"Error fetching NOTAMs for {icao_code}: {e}")
        raise NotamServiceError(f"Failed to retrieve NOTAMs: {e}")
    except Exception as e:
        print(f"Error parsing NOTAMs for {icao_code}: {e}")
        raise NotamServiceError(f"Failed to parse NOTAMs: {e}")

if __name__ == "__main__":
    print("--- Testing NOTAM Service ---")
    try:
        notams = get_notams("KSFO")
        print(f"Found {len(notams)} NOTAMs for KSFO")
        for notam in notams:
            print(f"\nNOTAM {notam['number']}:")
            print(f"Type: {notam['type']}")
            print(f"Issued: {notam['issued']}")
            print(f"Text: {notam['text']}")
    except NotamServiceError as e:
        print(f"Caught NOTAM Service Error: {e}")
import os
from dotenv import load_dotenv
from zeep import Client
from zeep.wsse.username import UsernameToken
from typing import List, Dict, Any
from backend.core.cache import cache

load_dotenv()

FAA_USERNAME = os.getenv("FAA_USERNAME")
FAA_PASSWORD = os.getenv("FAA_PASSWORD")

WSDL_URL = "http://notamdemo.aim.nas.faa.gov/notamWFSservices/NOTAMDistributionService?wsdl"

class NotamServiceError(Exception):
    """Custom exception for NOTAM service errors."""
    pass

def get_notams(icao_code: str) -> List[Dict[str, Any]]:
    """
    Fetches NOTAMs for a given ICAO code from the FAA NOTAM SOAP API.

    Args:
        icao_code: The ICAO code of the airport.

    Returns:
        A list of dictionaries, where each dictionary represents a NOTAM.
        Returns an empty list if the request fails or no NOTAMs are found.
    """
    cache_key = f"notams_{icao_code}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        client = Client(WSDL_URL, wsse=UsernameToken(FAA_USERNAME, FAA_PASSWORD))
        response = client.service.getNotamByIcao(icaoCode=icao_code)
        # The response object from zeep is not directly serializable to JSON.
        # We need to extract the relevant data into a list of dictionaries.
        result = []
        if response and hasattr(response, 'notam'):
            for notam in response.notam:
                result.append({
                    'text': notam.text
                })
        cache.set(cache_key, result)
        return result
    except Exception as e:
        print(f"Error fetching NOTAMs for {icao_code}: {e}")
        raise NotamServiceError(f"Failed to retrieve NOTAMs: {e}")

if __name__ == "__main__":
    print("--- Testing NOTAM Service ---")
    try:
        notams = get_notams("KSFO")
        print(f"NOTAMs for KSFO: {notams}")
    except NotamServiceError as e:
        print(f"Caught NOTAM Service Error: {e}")
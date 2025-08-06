import requests
from typing import List, Dict, Any

def get_notams(icao_code: str) -> List[Dict[str, Any]]:
    """
    Fetches NOTAMs for a given ICAO code from the NASA NOTAM API.

    Args:
        icao_code: The ICAO code of the airport.

    Returns:
        A list of dictionaries, where each dictionary represents a NOTAM.
        Returns an empty list if the request fails or no NOTAMs are found.
    """
    # Note: The NASA NOTAM API endpoint and parameters are based on online documentation
    # and may need to be adjusted.
    url = f"https://notams.aim.nas.nasa.gov/api/v1/notams?location={icao_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NOTAMs for {icao_code}: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding NOTAMs JSON for {icao_code}: {e}")
        return []

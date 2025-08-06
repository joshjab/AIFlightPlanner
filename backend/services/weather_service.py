import requests

AWC_API_BASE_URL = "https://aviationweather.gov/api/data"

def get_weather_data(icao_code: str) -> dict:
    """Fetches METAR and TAF data for a given ICAO code from the AWC API."""
    metar_url = f"{AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    taf_url = f"{AWC_API_BASE_URL}/taf?ids={icao_code}&format=json"

    try:
        metar_response = requests.get(metar_url)
        metar_response.raise_for_status() # Raise an exception for bad status codes
        metar_data = metar_response.json()

        taf_response = requests.get(taf_url)
        taf_response.raise_for_status()
        taf_data = taf_response.json()

        return {
            "metar": metar_data[0]["rawOb"] if metar_data else "",
            "taf": taf_data[0]["rawTAF"] if taf_data else ""
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {icao_code}: {e}")
        return {"metar": "", "taf": ""}

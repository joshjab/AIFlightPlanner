import requests
from backend.core.cache import cache

AWC_API_BASE_URL = "https://aviationweather.gov/api/data"

def get_weather_data(icao_code: str) -> dict:
    """Fetches METAR and TAF data for a given ICAO code from the AWC API."""
    cache_key = f"weather_data_{icao_code}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    metar_url = f"{AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    taf_url = f"{AWC_API_BASE_URL}/taf?ids={icao_code}&format=json"

    empty_result = {"metar": "", "taf": ""}
    metar_data = {}
    taf_data = {}

    try:
        # Get METAR data
        try:
            metar_response = requests.get(metar_url)
            metar_response.raise_for_status()
            metar_data = metar_response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            print(f"Error fetching METAR data for {icao_code}: {e}")
            metar_data = []

        # Get TAF data
        try:
            taf_response = requests.get(taf_url)
            taf_response.raise_for_status()
            taf_data = taf_response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            print(f"Error fetching TAF data for {icao_code}: {e}")
            taf_data = []

        # If both requests failed, return empty result
        if not metar_data and not taf_data:
            return empty_result

        result = {
            "metar": metar_data[0]["rawOb"] if metar_data else "",
            "taf": taf_data[0]["rawTAF"] if taf_data else ""
        }
        cache.set(cache_key, result)
        return result

    except Exception as e:
        print(f"Error processing weather data for {icao_code}: {e}")
        return empty_result

def get_enroute_weather_warnings() -> list[str]:
    """Fetches enroute weather warnings (SIGMETs) from the AWC API."""
    cache_key = "enroute_weather_warnings"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    sigmet_url = f"{AWC_API_BASE_URL}/airsigmet?format=json"
    try:
        response = requests.get(sigmet_url)
        response.raise_for_status()
        sigmet_data = response.json()
        result = [sigmet.get("rawSigmet", "") for sigmet in sigmet_data]

        # Cache successful results
        if result:
            cache.set(cache_key, result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SIGMETs: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding SIGMET response: {e}")
        return []
        cache.set(cache_key, result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SIGMETs: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding SIGMETs JSON response: {e}")
        return []

if __name__ == "__main__":
    print("--- Testing Weather Service ---")
    weather_data = get_weather_data("KSFO")
    print(f"Weather data for KSFO: {weather_data}")
    enroute_warnings = get_enroute_weather_warnings()
    print(f"Enroute weather warnings: {enroute_warnings}")

import pytest
import requests
import requests_mock
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import weather_service, notam_service
from core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    cache._cache = {}


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m


def test_get_weather_data_success(mock_requests):
    icao_code = "KLAX"
    metar_url = f"{weather_service.AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    taf_url = f"{weather_service.AWC_API_BASE_URL}/taf?ids={icao_code}&format=json"

    mock_requests.get(metar_url, json=[{"rawOb": "METAR KLAX ..."}])
    mock_requests.get(taf_url, json=[{"rawTAF": "TAF KLAX ..."}])

    weather_data = weather_service.get_weather_data(icao_code)

    assert weather_data["metar"] == "METAR KLAX ..."
    assert weather_data["taf"] == "TAF KLAX ..."


def test_get_weather_data_request_exception(mock_requests):
    icao_code = "KLAX"
    metar_url = f"{weather_service.AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    taf_url = f"{weather_service.AWC_API_BASE_URL}/taf?ids={icao_code}&format=json"
    mock_requests.get(metar_url, exc=requests.exceptions.RequestException)
    mock_requests.get(taf_url, exc=requests.exceptions.RequestException)

    weather_data = weather_service.get_weather_data(icao_code)

    assert weather_data["metar"] == ""
    assert weather_data["taf"] == ""


def test_get_weather_data_json_decode_error(mock_requests):
    icao_code = "KLAX"
    metar_url = f"{weather_service.AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    taf_url = f"{weather_service.AWC_API_BASE_URL}/taf?ids={icao_code}&format=json"
    mock_requests.get(metar_url, text="invalid json")
    mock_requests.get(taf_url, text="invalid json")

    weather_data = weather_service.get_weather_data(icao_code)

    assert weather_data["metar"] == ""
    assert weather_data["taf"] == ""


def test_get_enroute_weather_warnings_success(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/airsigmet?format=json"
    mock_requests.get(sigmet_url, json=[{"rawSigmet": "SIGMET ..."}])

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == ["SIGMET ..."]


def test_get_enroute_weather_warnings_request_exception(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/airsigmet?format=json"
    mock_requests.get(sigmet_url, exc=requests.exceptions.RequestException)

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == []


def test_get_enroute_weather_warnings_json_decode_error(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/airsigmet?format=json"
    mock_requests.get(sigmet_url, text="invalid json")

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == []


def test_get_notams_success(mock_requests):
    """Test successful NOTAM retrieval and parsing."""
    # Mock the initialization requests
    mock_requests.get(f"{notam_service.BASE_URL}/notamSearch/", text="OK")
    mock_requests.get(notam_service.APP_URL, text="OK")
    
    # Mock the NOTAM API response
    mock_response = {
        "notamList": [
            {
                "notamNumber": "1/2345",
                "featureName": "OBST",
                "issueDate": "10/20/2025 1200",
                "startDate": "10/20/2025 1200",
                "endDate": "10/21/2025 1200",
                "traditionalMessage": "CRANE 150FT AGL 2NM NORTH OF RWY",
                "status": "ACTIVE",
                "icaoMessage": "NOTAM TEXT",
                "plainLanguageMessage": "NOTAM TEXT",
                "facilityDesignator": "KSFO",
                "icaoId": "KSFO",
                "airportName": "SAN FRANCISCO INTL",
                "keyword": "OBST",
                "cancelledOrExpired": False
            },
            {
                "notamNumber": "1/2346",
                "featureName": "RWY",
                "issueDate": "10/20/2025 1300",
                "startDate": "10/20/2025 1300",
                "endDate": "10/21/2025 1300",
                "traditionalMessage": "RWY 28L CLSD",
                "status": "ACTIVE",
                "icaoMessage": "NOTAM TEXT",
                "plainLanguageMessage": "NOTAM TEXT",
                "facilityDesignator": "KSFO",
                "icaoId": "KSFO",
                "airportName": "SAN FRANCISCO INTL",
                "keyword": "RWY",
                "cancelledOrExpired": False
            }
        ],
        "totalNotamCount": 2
    }
    mock_requests.post(notam_service.SEARCH_URL, json=mock_response)

    notams = notam_service.get_notams("KSFO")

    assert len(notams) == 2
    assert notams[0]["number"] == "1/2345"
    assert notams[0]["type"] == "OBST"
    assert notams[0]["issued"] == "2025-10-20T12:00:00"
    assert notams[0]["text"] == "CRANE 150FT AGL 2NM NORTH OF RWY"
    assert notams[1]["number"] == "1/2346"


def test_get_notams_network_error(mock_requests):
    """Test NOTAM retrieval with network error."""
    # Mock initialization
    mock_requests.get(f"{notam_service.BASE_URL}/notamSearch/", text="OK")
    mock_requests.get(notam_service.APP_URL, text="OK")
    
    # Mock search with error
    mock_requests.post(notam_service.SEARCH_URL, exc=requests.exceptions.RequestException)

    with pytest.raises(notam_service.NotamServiceError, match="Failed to retrieve NOTAMs"):
        notam_service.get_notams("KSFO")


def test_get_notams_caching(mock_requests):
    """Test that NOTAMs are properly cached."""
    # Mock initialization
    mock_requests.get(f"{notam_service.BASE_URL}/notamSearch/", text="OK")
    mock_requests.get(notam_service.APP_URL, text="OK")
    
    # Mock NOTAM response
    mock_response = {
        "notamList": [
            {
                "notamNumber": "1/2345",
                "featureName": "OBST",
                "issueDate": "10/20/2025 1200",
                "startDate": "10/20/2025 1200",
                "endDate": "10/21/2025 1200",
                "traditionalMessage": "CRANE 150FT AGL 2NM NORTH OF RWY",
                "status": "ACTIVE",
                "icaoMessage": "NOTAM TEXT",
                "plainLanguageMessage": "NOTAM TEXT",
                "facilityDesignator": "KSFO",
                "icaoId": "KSFO",
                "airportName": "SAN FRANCISCO INTL",
                "keyword": "OBST",
                "cancelledOrExpired": False
            }
        ],
        "totalNotamCount": 1
    }
    mock_requests.post(notam_service.SEARCH_URL, json=mock_response)

    # First call should hit the network
    first_result = notam_service.get_notams("KSFO")
    assert len(first_result) == 1
    assert first_result[0]["number"] == "1/2345"

    # Second call should use cached data
    mock_requests.reset_mock()  # Clear request history
    second_result = notam_service.get_notams("KSFO")
    assert second_result == first_result
    assert not mock_requests.called  # No new requests should have been made


def test_get_notams_json_decode_error(mock_requests):
    """Test NOTAM retrieval with invalid JSON response."""
    # Mock initialization
    mock_requests.get(f"{notam_service.BASE_URL}/notamSearch/", text="OK")
    mock_requests.get(notam_service.APP_URL, text="OK")
    
    # Mock search with invalid JSON
    mock_requests.post(notam_service.SEARCH_URL, text="invalid json")

    notams = notam_service.get_notams("KLAX")

    assert notams == []
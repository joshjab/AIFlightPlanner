import pytest
import requests
import requests_mock
from backend.services import weather_service, notam_service
from backend.core.cache import cache


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
    mock_requests.get(metar_url, exc=requests.exceptions.RequestException)

    weather_data = weather_service.get_weather_data(icao_code)

    assert weather_data["metar"] == ""
    assert weather_data["taf"] == ""


def test_get_weather_data_json_decode_error(mock_requests):
    icao_code = "KLAX"
    metar_url = f"{weather_service.AWC_API_BASE_URL}/metar?ids={icao_code}&format=json"
    mock_requests.get(metar_url, text="invalid json")

    weather_data = weather_service.get_weather_data(icao_code)

    assert weather_data["metar"] == ""
    assert weather_data["taf"] == ""


def test_get_enroute_weather_warnings_success(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/sigmet?format=json"
    mock_requests.get(sigmet_url, json=[{"rawSigmet": "SIGMET ..."}])

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == ["SIGMET ..."]


def test_get_enroute_weather_warnings_request_exception(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/sigmet?format=json"
    mock_requests.get(sigmet_url, exc=requests.exceptions.RequestException)

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == []


def test_get_enroute_weather_warnings_json_decode_error(mock_requests):
    sigmet_url = f"{weather_service.AWC_API_BASE_URL}/sigmet?format=json"
    mock_requests.get(sigmet_url, text="invalid json")

    warnings = weather_service.get_enroute_weather_warnings()

    assert warnings == []


def test_get_notams_success(mock_requests):
    icao_code = "KLAX"
    notam_url = f"https://notams.aim.nas.nasa.gov/api/v1/notams?location={icao_code}"
    mock_requests.get(notam_url, json={"items": [{"text": "NOTAM 1"}, {"text": "NOTAM 2"}]})

    notams = notam_service.get_notams(icao_code)

    assert notams == [{"text": "NOTAM 1"}, {"text": "NOTAM 2"}]


def test_get_notams_request_exception(mock_requests):
    icao_code = "KLAX"
    notam_url = f"https://notams.aim.nas.nasa.gov/api/v1/notams?location={icao_code}"
    mock_requests.get(notam_url, exc=requests.exceptions.RequestException)

    notams = notam_service.get_notams(icao_code)

    assert notams == []


def test_get_notams_json_decode_error(mock_requests):
    icao_code = "KLAX"
    notam_url = f"https://notams.aim.nas.nasa.gov/api/v1/notams?location={icao_code}"
    mock_requests.get(notam_url, text="invalid json")

    notams = notam_service.get_notams(icao_code)

    assert notams == []
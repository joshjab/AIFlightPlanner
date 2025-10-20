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


def test_notam_session_initialization_success(mock_requests):
    """Test successful initialization of NOTAM session."""
    mock_requests.get(
        notam_service.APP_URL,
        text="<html></html>",
        cookies={
            "JSESSIONID": "test-session-id",
            "JSESSIONIDXSRF": "test-xsrf-token"
        }
    )

    session = notam_service.NotamSession()
    assert session.initialize() == True
    assert session.is_initialized() == True


def test_notam_session_initialization_failure(mock_requests):
    """Test NOTAM session initialization failure."""
    mock_requests.get(notam_service.APP_URL, status_code=500)

    session = notam_service.NotamSession()
    with pytest.raises(notam_service.NotamServiceError, match="Session initialization failed"):
        session.initialize()


def test_get_notams_success(mock_requests):
    """Test successful NOTAM retrieval and parsing."""
    # Mock the initial session setup
    mock_requests.get(
        notam_service.APP_URL,
        text="<html></html>",
        cookies={
            "JSESSIONID": "test-session-id",
            "JSESSIONIDXSRF": "test-xsrf-token"
        }
    )

    # Mock the NOTAM search response
    mock_html = """
    <div class="notam-results">
        <div class="notam-number">FDC 1/2345</div>
        <div class="notam-type">OBST</div>
        <div class="notam-issued">10/20/2025 1200Z</div>
        <div class="notam-text">CRANE 150FT AGL 2NM NORTH OF RWY</div>
    </div>
    <div class="notam-results">
        <div class="notam-number">FDC 1/2346</div>
        <div class="notam-type">RWY</div>
        <div class="notam-issued">10/20/2025 1300Z</div>
        <div class="notam-text">RWY 28L CLSD</div>
    </div>
    """
    mock_requests.post(notam_service.SEARCH_URL, text=mock_html)

    notams = notam_service.get_notams("KSFO")

    assert len(notams) == 2
    assert notams[0]["number"] == "FDC 1/2345"
    assert notams[0]["type"] == "OBST"
    assert notams[0]["issued"] == "10/20/2025 1200Z"
    assert notams[0]["text"] == "CRANE 150FT AGL 2NM NORTH OF RWY"
    assert notams[1]["number"] == "FDC 1/2346"


def test_get_notams_network_error(mock_requests):
    """Test NOTAM retrieval with network error."""
    mock_requests.get(notam_service.APP_URL, text="<html></html>", cookies={"JSESSIONID": "test"})
    mock_requests.post(notam_service.SEARCH_URL, exc=requests.exceptions.RequestException)

    with pytest.raises(notam_service.NotamServiceError, match="Failed to retrieve NOTAMs"):
        notam_service.get_notams("KSFO")


def test_get_notams_caching(mock_requests):
    """Test that NOTAMs are properly cached."""
    # Mock successful session initialization
    mock_requests.get(
        notam_service.APP_URL,
        text="<html></html>",
        cookies={"JSESSIONID": "test", "JSESSIONIDXSRF": "test"}
    )

    # Mock NOTAM response
    mock_html = """
    <div class="notam-results">
        <div class="notam-number">FDC 1/2345</div>
        <div class="notam-type">OBST</div>
        <div class="notam-issued">10/20/2025 1200Z</div>
        <div class="notam-text">CRANE 150FT AGL 2NM NORTH OF RWY</div>
    </div>
    """
    mock_requests.post(notam_service.SEARCH_URL, text=mock_html)

    # First call should hit the network
    first_result = notam_service.get_notams("KSFO")
    assert len(first_result) == 1
    assert first_result[0]["number"] == "FDC 1/2345"

    # Second call should use cached data
    mock_requests.reset_mock()  # Clear request history
    second_result = notam_service.get_notams("KSFO")
    assert second_result == first_result
    assert not mock_requests.called  # No new requests should have been made


def test_get_notams_json_decode_error(mock_requests):
    icao_code = "KLAX"
    notam_url = f"https://notams.aim.nas.nasa.gov/api/v1/notams?location={icao_code}"
    mock_requests.get(notam_url, text="invalid json")

    notams = notam_service.get_notams(icao_code)

    assert notams == []
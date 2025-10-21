"""
Unit tests for the FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from backend.schemas import Airport
from backend.services.notam_service import NotamServiceError

from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the /health endpoint returns ok"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.fixture
def mock_metar():
    return "KXXX 201753Z 18010KT 10SM FEW050 25/15 A2992"

@pytest.fixture
def mock_taf():
    return "KXXX 201700Z 2018/2118 18012KT P6SM FEW050"

@pytest.fixture
def mock_weather_data(mock_metar, mock_taf):
    return {
        "metar": mock_metar,
        "taf": mock_taf
    }

@pytest.fixture
def mock_notams():
    return [
        {"id": "NOTAM1", "text": "Test NOTAM 1"},
        {"id": "NOTAM2", "text": "Test NOTAM 2"}
    ]

@pytest.fixture
def mock_airport_details():
    return {
        "icao": "KXXX",
        "name": "Test Airport",
        "latitude": 40.0,
        "longitude": -104.0,
        "elevation": 5000
    }

def test_briefing_endpoint_success(mock_weather_data, mock_notams, mock_airport_details):
    """Test successful briefing generation"""
    # Create a departure and destination version of the data
    dep_details = mock_airport_details.copy()
    dest_details = mock_airport_details.copy()
    dest_details["icao"] = "KYYY"

    # Create mock Airport objects
    mock_dep_airport = Mock()
    mock_dep_airport.to_dict.return_value = dep_details
    mock_dest_airport = Mock()
    mock_dest_airport.to_dict.return_value = dest_details

    # Create mock database session
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.first.side_effect = lambda: mock_dep_airport if mock_session.query.call_args[0][0] == Airport and mock_session.query.return_value.filter.call_args[0][0].right.value == "KXXX" else mock_dest_airport

    with (
        patch('backend.services.weather_service.get_weather_data', return_value=mock_weather_data),
        patch('backend.services.notam_service.get_notams', return_value=mock_notams),
        patch('backend.services.airport_service.SessionLocal', return_value=mock_session)
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "route" in data
        assert "weather" in data
        assert "notams" in data
        
        # Check weather
        assert "departure" in data["weather"]
        assert "destination" in data["weather"]
        assert data["weather"]["departure"]["metar"] == mock_weather_data["metar"]
        assert data["weather"]["destination"]["metar"] == mock_weather_data["metar"]  # Using same mock data for both
        
        # Check NOTAMs
        assert len(data["notams"]["departure"]) == len(mock_notams)
        assert len(data["notams"]["destination"]) == len(mock_notams)
        assert data["notams"]["departure"][0]["id"] == mock_notams[0]["id"]
        assert data["notams"]["destination"][0]["id"] == mock_notams[0]["id"]

        # Check route info
        assert data["route"]["departure"] == "KXXX"
        assert data["route"]["destination"] == "KYYY"
        assert isinstance(data["route"]["distance"], (int, float))

def test_briefing_endpoint_invalid_airport():
    """Test briefing with invalid airport code"""
    response = client.get("/api/briefing?departure=KXX&destination=KYYY")  # Too short code
    assert response.status_code == 422  # Validation error

def test_briefing_endpoint_airport_not_found(mock_weather_data, mock_notams):
    """Test briefing when airport is not found"""
    # Mock session that returns None for any airport query
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = None

    with (
        patch('backend.services.airport_service.SessionLocal', return_value=mock_session),
        patch('backend.services.weather_service.get_weather_data', return_value=mock_weather_data),
        patch('backend.services.notam_service.get_notams', return_value=mock_notams)
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
        assert response.status_code == 404
        assert "Airport not found" in response.json()["detail"]

def test_briefing_endpoint_service_error(mock_airport_details, mock_weather_data):
    """Test briefing when a service fails"""
    # Create mock Airport object
    mock_airport = Mock()
    mock_airport.to_dict.return_value = mock_airport_details

    # Mock session that returns a valid airport
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = mock_airport

    with (
        patch('backend.services.airport_service.SessionLocal', return_value=mock_session),
        patch('backend.services.weather_service.get_weather_data', return_value=mock_weather_data),
        patch('backend.services.notam_service.get_notams', side_effect=NotamServiceError("NOTAM service down"))
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
        assert response.status_code == 503  # Service unavailable for NOTAM errors
        assert "NOTAM service error" in response.json()["detail"]

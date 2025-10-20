"""
Unit tests for the FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the /health endpoint returns ok"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.fixture
def mock_weather_data():
    return {
        "metar": "KXXX 201753Z 18010KT 10SM FEW050 25/15 A2992",
        "taf": "KXXX 201700Z 2018/2118 18012KT P6SM FEW050"
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
    
    with (
        patch('backend.services.weather_service.get_weather_data', return_value=mock_weather_data),
        patch('backend.services.notam_service.get_notams', return_value=mock_notams),
        patch('backend.services.airport_service.get_airport_by_icao', side_effect=lambda x: dep_details if x == "KXXX" else dest_details)
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
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
    with (
        patch('backend.services.airport_service.get_airport_by_icao', return_value=None),
        patch('backend.services.weather_service.get_weather_data', return_value=mock_weather_data),
        patch('backend.services.notam_service.get_notams', return_value=mock_notams)
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
        assert response.status_code == 404
        assert "Airport not found" in response.json()["detail"]

def test_briefing_endpoint_service_error(mock_airport_details):
    """Test briefing when a service fails"""
    with (
        patch('backend.services.airport_service.get_airport_by_icao', return_value=mock_airport_details),
        patch('backend.services.notam_service.get_notams', side_effect=Exception("NOTAM service down"))
    ):
        response = client.get("/api/briefing?departure=KXXX&destination=KYYY")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

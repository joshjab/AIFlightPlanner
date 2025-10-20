import pytest
from unittest.mock import patch, MagicMock

from backend.models.pilot_preferences import (
    PilotPreferences,
    PilotRatings,
    WeatherMinimums,
    FlightRules
)
from backend.services import recommendation_service

# Test data
VFR_CONDITIONS = {
    "ceiling": 4000,
    "visibility": 7,
    "wind_speed": 10,
    "wind_direction": 180,
    "runway_heading": 170,
    "flight_category": "VFR",
    "is_night": False
}

IFR_CONDITIONS = {
    "ceiling": 400,
    "visibility": 2,
    "wind_speed": 12,
    "wind_direction": 90,
    "runway_heading": 80,
    "flight_category": "IFR",
    "is_night": False
}

GOOD_NOTAMS = [
    "!KXXX 10/001 KXXX RWY 18/36 EDGE LIGHTING OTS",
    "!KXXX 10/002 KXXX TWY A CLSD"
]

BAD_NOTAMS = [
    "!KYYY 10/001 KYYY RWY ALL CLSD",
    "!KYYY 10/002 KYYY APCH ALL UNSAFE"
]

NO_WARNINGS = []

THUNDERSTORM_WARNINGS = [
    "SIGMET A1 VALID 201300/201700 THUNDERSTORMS OBSD MOVING EAST 25KT"
]

@pytest.fixture
def vfr_pilot_preferences():
    """Fixture for a VFR-only pilot's preferences"""
    return PilotPreferences(
        ratings=[PilotRatings.PRIVATE],
        flight_rules=FlightRules.VFR,
        day_minimums=WeatherMinimums(
            visibility_sm=5,
            ceiling_ft=3000,
            wind_speed_kts=15,
            crosswind_component_kts=8
        ),
        night_minimums=None,  # No night operations
        allow_rain=True,
        allow_snow=False,
        allow_thunderstorms_nearby=False
    )

@pytest.fixture
def ifr_pilot_preferences():
    """Fixture for an instrument-rated pilot's preferences"""
    return PilotPreferences(
        ratings=[PilotRatings.PRIVATE, PilotRatings.INSTRUMENT],
        flight_rules=FlightRules.IFR,
        day_minimums=WeatherMinimums(
            visibility_sm=2,
            ceiling_ft=1000,
            wind_speed_kts=20,
            crosswind_component_kts=12
        ),
        night_minimums=WeatherMinimums(
            visibility_sm=3,
            ceiling_ft=1500,
            wind_speed_kts=15,
            crosswind_component_kts=10
        ),
        allow_rain=True,
        allow_snow=True,
        allow_thunderstorms_nearby=False
    )

def test_vfr_pilot_in_vfr_conditions(vfr_pilot_preferences):
    """Test a VFR pilot in good VFR conditions should get a GO"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=VFR_CONDITIONS),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KXXX",
            "KXXX",
            vfr_pilot_preferences
        )
        
        assert go is True
        assert len(reasons) == 0

def test_vfr_pilot_in_ifr_conditions(vfr_pilot_preferences):
    """Test a VFR pilot in IFR conditions should get a NO-GO"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=IFR_CONDITIONS),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KYYY",
            "KYYY",
            vfr_pilot_preferences
        )
        
        assert go is False
        assert any("instrument rating" in reason.lower() for reason in reasons)
        assert any("ceiling" in reason.lower() for reason in reasons)
        assert any("visibility" in reason.lower() for reason in reasons)

def test_ifr_pilot_in_ifr_conditions(ifr_pilot_preferences):
    """Test an IFR pilot in IFR conditions should get a GO if within minimums"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=IFR_CONDITIONS),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KYYY",
            "KYYY",
            ifr_pilot_preferences
        )
        
        assert go is True
        assert len(reasons) == 0

def test_critical_notams(ifr_pilot_preferences):
    """Test that critical NOTAMs result in a NO-GO"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=VFR_CONDITIONS),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=BAD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KYYY",
            "KYYY",
            ifr_pilot_preferences
        )
        
        assert go is False
        assert any("CLSD" in reason or "UNSAFE" in reason for reason in reasons)

def test_thunderstorms_not_allowed(ifr_pilot_preferences):
    """Test that thunderstorms result in NO-GO when not allowed"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=VFR_CONDITIONS),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=THUNDERSTORM_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KXXX",
            "KXXX",
            ifr_pilot_preferences
        )
        
        assert go is False
        assert any("thunderstorm" in reason.lower() for reason in reasons)

def test_mixed_conditions(vfr_pilot_preferences):
    """Test with good departure but bad arrival conditions"""
    weather_data = {"metar": "test", "taf": "test"}
    with (
        patch('backend.services.recommendation_service._process_weather_data', side_effect=[VFR_CONDITIONS, IFR_CONDITIONS]),
        patch('backend.services.weather_service.get_weather_data', side_effect=[weather_data, weather_data]),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KXXX",  # Good VFR departure
            "KYYY",  # IFR arrival
            vfr_pilot_preferences
        )
        
        assert go is False
        assert any("arrival" in reason.lower() for reason in reasons)
        assert not any("departure" in reason.lower() for reason in reasons)

def test_night_operations_not_allowed(vfr_pilot_preferences):
    """Test that night operations are rejected when night minimums aren't specified"""
    night_conditions = VFR_CONDITIONS.copy()
    night_conditions["is_night"] = True
    weather_data = {"metar": "test", "taf": "test"}
    
    with (
        patch('backend.services.recommendation_service._process_weather_data', return_value=night_conditions),
        patch('backend.services.weather_service.get_weather_data', return_value=weather_data),
        patch('backend.services.weather_service.get_enroute_weather_warnings', return_value=NO_WARNINGS),
        patch('backend.services.notam_service.get_notams', return_value=GOOD_NOTAMS)
    ):
        go, reasons = recommendation_service.get_recommendation(
            "KXXX",
            "KXXX",
            vfr_pilot_preferences
        )
        
        assert go is False
        assert any("night" in reason.lower() for reason in reasons)

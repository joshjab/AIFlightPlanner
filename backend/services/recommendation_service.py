"""
This module contains the logic for generating Go/No-Go recommendations based on
pilot preferences, weather conditions, and airport information.
"""
from typing import Dict, List, Tuple
import math

from backend.models.pilot_preferences import PilotPreferences, PilotRatings, FlightRules
from backend.services import weather_service, airport_service, notam_service
from backend.utils.reason_formatter import (
    format_weather_reason,
    format_wind_reason,
    format_crosswind_reason,
    format_rating_reason,
    format_notam_reason,
    format_enroute_reason
)

def get_recommendation(
    departure_icao: str,
    arrival_icao: str,
    pilot_preferences: PilotPreferences
) -> Tuple[bool, List[str]]:
        """
        Generate a Go/No-Go recommendation based on pilot preferences and current conditions.

        Args:
            departure_icao: The ICAO code for the departure airport
            arrival_icao: The ICAO code for the arrival airport
            pilot_preferences: The pilot's preferences and minimums

        Returns:
            A tuple containing:
            - bool: True for "Go", False for "No-Go"
            - List[str]: List of reasons supporting the recommendation
        """
        reasons: List[str] = []
        
        # Get weather and airport conditions
        dep_weather = weather_service.get_weather_data(departure_icao)
        arr_weather = weather_service.get_weather_data(arrival_icao)
        enroute_warnings = weather_service.get_enroute_weather_warnings()

        # Get NOTAMs
        dep_notams = notam_service.get_notams(departure_icao)
        arr_notams = notam_service.get_notams(arrival_icao)

        # Process weather data into conditions
        dep_conditions = _process_weather_data(dep_weather, departure_icao)
        arr_conditions = _process_weather_data(arr_weather, arrival_icao)

        # Check basic weather minimums
        dep_go = _check_airport_conditions(
            dep_conditions,
            pilot_preferences,
            "Departure",
            reasons
        )
        arr_go = _check_airport_conditions(
            arr_conditions,
            pilot_preferences,
            "Arrival",
            reasons
        )

        # Check NOTAMs for critical issues
        if dep_go:
            dep_go = _check_notams(dep_notams, departure_icao, "Departure", reasons)
        if arr_go:
            arr_go = _check_notams(arr_notams, arrival_icao, "Arrival", reasons)

        # Check enroute conditions
        enroute_go = _check_enroute_conditions(
            enroute_warnings,
            departure_icao,
            arrival_icao,
            pilot_preferences,
            reasons
        )

        # Overall recommendation is "Go" only if all checks pass
        return (dep_go and arr_go and enroute_go), reasons

def _check_airport_conditions(
    conditions: Dict,
    preferences: PilotPreferences,
    airport_type: str,
    reasons: List[str]
) -> bool:
    """
    Check if the conditions at an airport meet the pilot's minimums.

    Args:
        conditions: The current airport conditions
        preferences: The pilot's preferences and minimums
        airport_type: String indicating "Departure" or "Arrival"
        reasons: List to append recommendation reasons to

    Returns:
        bool: True if conditions meet minimums, False otherwise
    """
    go = True

    # Get appropriate minimums based on time of day
    minimums = preferences.night_minimums if conditions["is_night"] else preferences.day_minimums
    if conditions["is_night"] and preferences.night_minimums is None:
        go = False
        reasons.append(
            f"{airport_type} conditions will be night, "
            "but pilot has not specified night minimums"
        )
        return go

    # Check ceiling against pilot minimums
    if conditions["ceiling"] < minimums.ceiling_ft:
        go = False
        reasons.append(
            format_weather_reason(
                "ceiling",
                conditions["ceiling"],
                minimums.ceiling_ft,
                "ft",
                airport_type
            )
        )

    # Check visibility against pilot minimums
    if conditions["visibility"] < minimums.visibility_sm:
        go = False
        reasons.append(
            format_weather_reason(
                "visibility",
                conditions["visibility"],
                minimums.visibility_sm,
                "SM",
                airport_type
            )
        )

    # Check wind conditions
    max_wind = minimums.wind_speed_kts
    if conditions["wind_speed"] > max_wind:
        go = False
        reasons.append(
            format_wind_reason(
                conditions["wind_speed"],
                conditions["wind_direction"],
                conditions.get("gust_speed"),
                max_wind,
                airport_type
            )
        )

    # Check crosswind component if specified
    if minimums.crosswind_component_kts:
        crosswind = _calculate_crosswind(
            conditions["wind_direction"],
            conditions["wind_speed"],
            conditions["runway_heading"]
        )
        if crosswind > minimums.crosswind_component_kts:
            go = False
            reasons.append(
                format_crosswind_reason(
                    crosswind,
                    minimums.crosswind_component_kts,
                    airport_type,
                    conditions.get("runway", "in use")
                )
            )

    # If pilot doesn't have an instrument rating but requesting IFR, that's a no-go
    if preferences.flight_rules == FlightRules.IFR and PilotRatings.INSTRUMENT not in preferences.ratings:
        go = False
        reasons.append(
            format_rating_reason(
                "IFR",
                "an instrument rating",
                None  # This applies to the whole flight
            )
        )

    # If pilot is VFR only and conditions are not VFR, that's a no-go
    if PilotRatings.INSTRUMENT not in preferences.ratings and conditions["flight_category"] != "VFR":
        go = False
        reasons.append(
            format_rating_reason(
                conditions["flight_category"],
                "an instrument rating",
                airport_type
            )
        )    
    return go

def _check_notams(notams: List[str], icao: str, airport_type: str, reasons: List[str]) -> bool:
    """
    Check NOTAMs for critical issues that would prevent flight.

    Args:
        notams: List of NOTAMs for the airport
        icao: Airport ICAO code
        airport_type: String indicating "Departure" or "Arrival"
        reasons: List to append recommendation reasons to

    Returns:
        bool: True if NOTAMs don't prevent flight, False otherwise
    """
    go = True

    critical_keywords = [
        "CLSD",  # Airport/runway closed
        "UNSAFE",  # Unsafe condition
        "NOTAM A",  # Airport closed to all operations
        "RWY UNUSABLE",  # Runway unusable
        "NO LANDING",  # Landing not permitted
    ]

    for notam in notams:
        for keyword in critical_keywords:
            if keyword in notam.upper():
                go = False
                reasons.append(format_notam_reason(notam, airport_type))

    return go

def _check_enroute_conditions(
    warnings: List[str],
    departure_icao: str,
    arrival_icao: str,
    preferences: PilotPreferences,
    reasons: List[str]
) -> bool:
    """
    Check enroute conditions for potential hazards.

    Args:
        warnings: List of enroute weather warnings
        departure_icao: Departure airport ICAO code
        arrival_icao: Arrival airport ICAO code
        preferences: Pilot preferences including weather tolerance
        reasons: List to append recommendation reasons to

    Returns:
        bool: True if enroute conditions are acceptable, False otherwise
    """
    go = True

    for warning in warnings:
        warning_upper = warning.upper()
        
        warning_type = "SIGMET" if "SIGMET" in warning_upper else "AIRMET"
        
        # Check for thunderstorms if pilot prefers to avoid them
        if not preferences.allow_thunderstorms_nearby and "THUNDERSTORM" in warning_upper:
            go = False
            reasons.append(format_enroute_reason("thunderstorms", warning_type, warning))
            
        # Check precipitation type against preferences
        if not preferences.allow_rain and "RAIN" in warning_upper:
            go = False
            reasons.append(format_enroute_reason("rain", warning_type, warning))
            
        if not preferences.allow_snow and "SNOW" in warning_upper:
            go = False
            reasons.append(format_enroute_reason("snow", warning_type, warning))
            
        # Always warn about severe conditions
        if any(hazard in warning_upper for hazard in ["TORNADO", "HURRICANE", "SEVERE TURBULENCE"]):
            go = False
            reasons.append(format_enroute_reason("severe weather", warning_type, warning))

    return go

def _process_weather_data(weather_data: Dict, icao_code: str) -> Dict:
    """
    Process raw weather data into a conditions dictionary.

    Args:
        weather_data: Raw weather data from weather service
        icao_code: Airport ICAO code for error messages

    Returns:
        Dict containing processed conditions
    """
    # For now, using mock data - we'll need to actually parse the METAR
    # This should be enhanced to properly parse the METAR string
    metar = weather_data.get("metar", "")
    
    # TODO: Add proper METAR parsing
    # For now returning mock data - this should be replaced with actual parsing
    return {
        "ceiling": 3000,  # This should come from METAR ceiling
        "visibility": 5,  # This should come from METAR visibility
        "wind_speed": 10,  # This should come from METAR wind
        "wind_direction": 180,  # This should come from METAR wind
        "runway_heading": 170,  # This should come from airport data
        "flight_category": "VFR",  # This should be calculated from ceiling/visibility
        "is_night": False  # This should be calculated based on current time and location
    }

def _calculate_crosswind(
    wind_direction: int,
    wind_speed: float,
    runway_heading: int
) -> float:
    """
    Calculate the crosswind component for a given wind and runway.

    Args:
        wind_direction: Wind direction in degrees
        wind_speed: Wind speed in knots
        runway_heading: Runway heading in degrees

    Returns:
        float: Crosswind component in knots
    """
    angle = abs(wind_direction - runway_heading)
    if angle > 180:
        angle = 360 - angle
    return abs(wind_speed * math.sin(math.radians(angle)))


if __name__ == "__main__":
    from backend.models.pilot_preferences import (
        PilotPreferences,
        PilotRatings,
        WeatherMinimums,
        FlightRules
    )

    def test_recommendation_service():
        # Create sample pilot preferences
        preferences = PilotPreferences(
            ratings=[PilotRatings.PRIVATE],  # VFR only pilot
            flight_rules=FlightRules.VFR,
            day_minimums=WeatherMinimums(
                visibility_sm=5,
                ceiling_ft=3000,
                wind_speed_kts=15,
                crosswind_component_kts=8
            ),
            # Optional fields with defaults
            night_minimums=None,  # No night operations
            allow_rain=True,
            allow_snow=False,
            allow_thunderstorms_nearby=False
        )

        # Store original get_weather_data function
        original_get_weather = weather_service.get_weather_data

        # Create mock weather data function
        # Store original service functions
        original_get_weather = weather_service.get_weather_data
        original_get_warnings = weather_service.get_enroute_weather_warnings
        original_get_notams = notam_service.get_notams

        # Create mock weather function
        def mock_get_weather(icao: str):
            # Return good VFR conditions for KXXX and marginal VFR for KYYY
            if icao == "KXXX":
                return {
                    "metar": "KXXX 201253Z 18010KT 7SM FEW040 22/14 A3001",
                    "taf": "KXXX 201200Z 2012/2112 18012KT P6SM FEW040"
                }
            else:
                return {
                    "metar": "KYYY 201253Z 09012KT 4SM BR BKN025 18/16 A2992",
                    "taf": "KYYY 201200Z 2012/2112 09010KT 4SM BR BKN025"
                }

        # Create mock enroute warnings function
        def mock_get_warnings():
            return [
                "AIRMET TANGO VALID UNTIL 210300 FOR TURB... MOD TURB BLW FL180",
                "SIGMET A1 VALID 201300/201700 THUNDERSTORMS OBSD MOVING EAST 25KT"
            ]

        # Create mock NOTAMs function
        def mock_get_notams(icao: str):
            if icao == "KXXX":
                return [
                    "!KXXX 10/001 KXXX RWY 18/36 EDGE LIGHTING OTS",
                    "!KXXX 10/002 KXXX TWY A CLSD"
                ]
            else:
                return [
                    "!KYYY 10/001 KYYY FUEL UNAVBL",
                    "!KYYY 10/002 KYYY BIRDS VICINITY OF RWY"
                ]

        # Replace the real functions with our mocks
        weather_service.get_weather_data = mock_get_weather
        weather_service.get_enroute_weather_warnings = mock_get_warnings
        notam_service.get_notams = mock_get_notams

        try:
            # Test the service with our mock data
            go, reasons = get_recommendation("KXXX", "KYYY", preferences)

            print(f"\nRecommendation: {'GO' if go else 'NO-GO'}")
            print("\nReasons:")
            for reason in reasons:
                print(f"- {reason}")
        
        finally:
            # Restore original functions
            weather_service.get_weather_data = original_get_weather
            weather_service.get_enroute_weather_warnings = original_get_warnings
            notam_service.get_notams = original_get_notams

    # Run the test
    test_recommendation_service()

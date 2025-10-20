"""
This module contains the logic for generating Go/No-Go recommendations based on
pilot preferences, weather conditions, and airport information.
"""
from typing import Dict, List, Tuple
import math

from backend.models.pilot_preferences import PilotPreferences
from backend.services import weather_service, airport_service, notam_service

async def get_recommendation(
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
        
        # Get current conditions for both airports
        dep_weather = weather_service.get_weather_data(departure_icao)
        arr_weather = weather_service.get_weather_data(arrival_icao)

        # Process weather data into conditions
        dep_conditions = _process_weather_data(dep_weather, departure_icao)
        arr_conditions = _process_weather_data(arr_weather, arrival_icao)

        # Check weather minimums against pilot preferences
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

        # Overall recommendation is "Go" only if both airports pass checks
        return (dep_go and arr_go), reasons

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
            f"{airport_type} airport ceiling {conditions['ceiling']}ft "
            f"below pilot minimum of {minimums.ceiling_ft}ft"
        )

    # Check visibility against pilot minimums
    if conditions["visibility"] < minimums.visibility_sm:
        go = False
        reasons.append(
            f"{airport_type} airport visibility {conditions['visibility']}SM "
            f"below pilot minimum of {minimums.visibility_sm}SM"
        )

    # Check wind conditions
    max_wind = minimums.wind_speed_kts
    if conditions["wind_speed"] > max_wind:
        go = False
        reasons.append(
            f"{airport_type} airport wind speed {conditions['wind_speed']}kts "
            f"exceeds pilot maximum of {max_wind}kts"
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
                f"{airport_type} airport crosswind component {crosswind}kts "
                f"exceeds pilot maximum of {minimums.crosswind_component_kts}kts"
            )

    # If pilot doesn't have an instrument rating but requesting IFR, that's a no-go
    if preferences.flight_rules == FlightRules.IFR and PilotRatings.INSTRUMENT not in preferences.ratings:
        go = False
        reasons.append(
            f"IFR flight requested but pilot does not have an instrument rating"
        )

    # If pilot is VFR only and conditions are not VFR, that's a no-go
    if PilotRatings.INSTRUMENT not in preferences.ratings and conditions["flight_category"] != "VFR":
        go = False
        reasons.append(
            f"{airport_type} airport conditions are {conditions['flight_category']} "
            "but pilot is not instrument rated"
        )

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
    import asyncio
    from backend.models.pilot_preferences import (
        PilotPreferences,
        PilotRatings,
        WeatherMinimums,
        FlightRules
    )

    async def test_recommendation_service():
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

        # Replace the real function with our mock
        weather_service.get_weather_data = mock_get_weather

        try:
            # Test the service with our mock data
            go, reasons = await get_recommendation("KXXX", "KYYY", preferences)

            print(f"\nRecommendation: {'GO' if go else 'NO-GO'}")
            print("\nReasons:")
            for reason in reasons:
                print(f"- {reason}")
        
        finally:
            # Restore original function
            weather_service.get_weather_data = original_get_weather

    # Run the test
    asyncio.run(test_recommendation_service())

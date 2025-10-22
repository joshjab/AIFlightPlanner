"""Utility functions for formatting recommendation reasons in a clear, human-readable way."""

from typing import Dict, List

def format_weather_reason(
    condition: str,
    actual: float,
    minimum: float,
    unit: str,
    airport_type: str
) -> str:
    """
    Format a weather-related reason with proper units and context.

    Args:
        condition: The type of weather condition (e.g., "ceiling", "visibility")
        actual: The actual observed value
        minimum: The minimum required value
        unit: The unit of measurement (e.g., "ft", "SM", "kts")
        airport_type: "Departure" or "Arrival"

    Returns:
        A formatted string explaining the weather condition
    """
    return (
        f"{airport_type} airport {condition} is {actual}{unit}, "
        f"which is below your minimum of {minimum}{unit}"
    )

def format_wind_reason(
    wind_speed: float,
    wind_direction: int,
    gust_speed: float | None,
    max_speed: float,
    airport_type: str
) -> str:
    """
    Format a wind-related reason with direction and gust information.

    Args:
        wind_speed: The sustained wind speed
        wind_direction: The wind direction in degrees
        gust_speed: The gust speed, if any
        max_speed: The maximum acceptable wind speed
        airport_type: "Departure" or "Arrival"

    Returns:
        A formatted string explaining the wind condition
    """
    wind_desc = f"{wind_speed}kts from {wind_direction}°"
    if gust_speed:
        wind_desc += f" gusting to {gust_speed}kts"
    
    return (
        f"{airport_type} airport winds are {wind_desc}, "
        f"which exceeds your maximum of {max_speed}kts"
    )

def format_crosswind_reason(
    crosswind: float,
    max_crosswind: float,
    airport_type: str,
    runway: str
) -> str:
    """
    Format a crosswind-related reason with runway information.

    Args:
        crosswind: The calculated crosswind component
        max_crosswind: The maximum acceptable crosswind
        airport_type: "Departure" or "Arrival"
        runway: The runway identifier

    Returns:
        A formatted string explaining the crosswind condition
    """
    return (
        f"{airport_type} airport runway {runway} has a {crosswind}kt crosswind component, "
        f"which exceeds your maximum of {max_crosswind}kts"
    )

def format_rating_reason(
    category: str,
    required_rating: str,
    airport_type: str | None = None
) -> str:
    """
    Format a pilot rating related reason.

    Args:
        category: The weather/flight category requiring the rating
        required_rating: The required rating
        airport_type: Optional airport type if specific to one airport

    Returns:
        A formatted string explaining the rating requirement
    """
    if airport_type:
        return (
            f"{airport_type} airport is reporting {category} conditions "
            f"which require {required_rating} privileges"
        )
    return f"This flight requires {required_rating} privileges due to {category} conditions"

def format_notam_reason(notam: dict, airport_type: str, level: str = "Critical") -> str:
    """
    Formats a NOTAM dictionary into a reason string.

    Args:
        notam: The NOTAM dictionary.
        airport_type: "Departure" or "Arrival".
        level: "Critical" or "Info".
    """
    try:
        notam_text = notam['traditional_message']
    except KeyError:
        notam_text = "Message not available"
    
    # Get the main condition text
    condition = notam_text.split(" ", 2)[2] if len(notam_text.split(" ")) > 2 else notam_text
    
    # Set the prefix based on the level
    prefix = "Critical NOTAM" if level == "Critical" else "Info NOTAM"

    return f"{airport_type} airport has {prefix}: {condition}"

def format_enroute_reason(
    condition: str,
    warning_type: str,
    full_text: str
) -> str:
    """
    Format an enroute weather warning reason.

    Args:
        condition: The specific weather condition
        warning_type: The type of warning (AIRMET/SIGMET)
        full_text: The complete warning text

    Returns:
        A formatted string explaining the enroute condition
    """
    return (
        f"Enroute {condition} reported - {warning_type}: {full_text}"
    )

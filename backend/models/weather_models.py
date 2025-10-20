"""Models for weather data and flight categories."""
from enum import Enum, auto

class FlightCategory(str, Enum):
    """Flight category based on ceiling and visibility."""
    VFR = "VFR"      # Ceiling > 3000ft and Visibility > 5SM
    MVFR = "MVFR"    # 1000ft ≤ Ceiling ≤ 3000ft and/or 3SM ≤ Visibility ≤ 5SM
    IFR = "IFR"      # 500ft ≤ Ceiling < 1000ft and/or 1SM ≤ Visibility < 3SM
    LIFR = "LIFR"    # Ceiling < 500ft and/or Visibility < 1SM

def determine_flight_category(ceiling_ft: float, visibility_sm: float) -> FlightCategory:
    """
    Determine the flight category based on ceiling and visibility.
    
    Args:
        ceiling_ft: Ceiling height in feet AGL
        visibility_sm: Visibility in statute miles
        
    Returns:
        FlightCategory: The determined flight category
    """
    if ceiling_ft < 500 or visibility_sm < 1:
        return FlightCategory.LIFR
    elif (ceiling_ft < 1000 or visibility_sm < 3):
        return FlightCategory.IFR
    elif (ceiling_ft <= 3000 or visibility_sm <= 5):
        return FlightCategory.MVFR
    else:
        return FlightCategory.VFR

def can_fly_vfr(conditions: dict) -> bool:
    """
    Determine if VFR flight is allowed based on conditions.
    
    Args:
        conditions: Dictionary containing weather conditions including:
            - ceiling_ft: Ceiling height in feet AGL
            - visibility_sm: Visibility in statute miles
            - is_night: Whether it is night time
            
    Returns:
        bool: True if VFR flight is allowed, False otherwise
    """
    # Standard VFR minimums
    if conditions["ceiling"] >= 3000 and conditions["visibility"] >= 5:
        return True
        
    # Special VFR minimums (daytime only)
    if not conditions["is_night"]:
        if conditions["visibility"] >= 1:
            # Would also need to check cloud clearance here,
            # but we don't have that data yet
            return True
            
    return False

"""Tests for weather models and flight category determination."""
import pytest
from backend.models.weather_models import (
    determine_flight_category,
    can_fly_vfr,
    FlightCategory
)

@pytest.mark.parametrize("ceiling,visibility,expected", [
    (3500, 7, FlightCategory.VFR),   # Clear VFR
    (2500, 4, FlightCategory.MVFR),  # MVFR due to both
    (3500, 4, FlightCategory.MVFR),  # MVFR due to visibility
    (2500, 6, FlightCategory.MVFR),  # MVFR due to ceiling
    (800, 2, FlightCategory.IFR),    # IFR conditions
    (400, 0.5, FlightCategory.LIFR), # Low IFR conditions
])
def test_determine_flight_category(ceiling, visibility, expected):
    """Test flight category determination for various conditions."""
    assert determine_flight_category(ceiling, visibility) == expected

@pytest.mark.parametrize("conditions,expected", [
    # Standard VFR conditions
    ({"ceiling": 3500, "visibility": 7, "is_night": False}, True),
    # Special VFR conditions (daytime)
    ({"ceiling": 1500, "visibility": 1.5, "is_night": False}, True),
    # Special VFR conditions at night (not allowed)
    ({"ceiling": 1500, "visibility": 1.5, "is_night": True}, False),
    # Below Special VFR minimums
    ({"ceiling": 1500, "visibility": 0.5, "is_night": False}, False),
])
def test_can_fly_vfr(conditions, expected):
    """Test VFR flight permission under various conditions."""
    assert can_fly_vfr(conditions) == expected

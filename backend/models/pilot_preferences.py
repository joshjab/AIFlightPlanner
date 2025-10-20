from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List


class FlightRules(str, Enum):
    """Flight rules that can be selected by the pilot."""
    VFR = "VFR"
    IFR = "IFR"
    SVFR = "SVFR"  # Special VFR


class PilotRatings(str, Enum):
    """Possible pilot ratings/certificates."""
    PRIVATE = "PRIVATE"
    COMMERCIAL = "COMMERCIAL"
    ATP = "ATP"
    INSTRUMENT = "INSTRUMENT"
    MULTI_ENGINE = "MULTI_ENGINE"


class WeatherMinimums(BaseModel):
    """Weather minimums specified by the pilot."""
    visibility_sm: float = Field(
        ...,  # Required field
        gt=0,  # Must be greater than 0
        description="Minimum visibility in statute miles"
    )
    ceiling_ft: int = Field(
        ...,  # Required field
        gt=0,  # Must be greater than 0
        description="Minimum ceiling height in feet AGL"
    )
    wind_speed_kts: int = Field(
        default=25,  # Default max wind of 25 knots
        gt=0,  # Must be greater than 0
        description="Maximum acceptable wind speed in knots"
    )
    crosswind_component_kts: Optional[int] = Field(
        default=None,
        gt=0,  # Must be greater than 0 if specified
        description="Maximum acceptable crosswind component in knots"
    )
    gusts_kts: Optional[int] = Field(
        default=None,
        gt=0,  # Must be greater than 0 if specified
        description="Maximum acceptable gust factor in knots"
    )

    @validator('crosswind_component_kts')
    def crosswind_less_than_wind(cls, v, values):
        """Ensure crosswind component is less than total wind speed."""
        if v is not None and v > values['wind_speed_kts']:
            raise ValueError('Crosswind component cannot be greater than total wind speed')
        return v

    @validator('gusts_kts')
    def gusts_greater_than_wind(cls, v, values):
        """Ensure gust value is greater than steady wind speed if specified."""
        if v is not None and v <= values['wind_speed_kts']:
            raise ValueError('Gust value must be greater than steady wind speed')
        return v


class PilotPreferences(BaseModel):
    """Main model for pilot preferences affecting go/no-go decisions."""
    flight_rules: FlightRules = Field(
        ...,  # Required field
        description="Intended flight rules for the flight"
    )
    ratings: List[PilotRatings] = Field(
        ...,  # Required field
        description="List of pilot ratings/certificates held"
    )
    day_minimums: WeatherMinimums = Field(
        ...,  # Required field
        description="Weather minimums for daytime operations"
    )
    night_minimums: Optional[WeatherMinimums] = Field(
        None,
        description="Weather minimums for night operations. If not specified, night operations are not desired."
    )
    allow_rain: bool = Field(
        default=True,
        description="Whether flight in rain is acceptable"
    )
    allow_snow: bool = Field(
        default=False,
        description="Whether flight in snow is acceptable"
    )
    allow_thunderstorms_nearby: bool = Field(
        default=False,
        description="Whether flight with thunderstorms in vicinity is acceptable"
    )
    max_elevation_ft: Optional[int] = Field(
        default=None,
        gt=0,  # Must be greater than 0 if specified
        description="Maximum field elevation in feet MSL the pilot is comfortable with"
    )
    prefer_towered: bool = Field(
        default=False,
        description="Whether towered airports are preferred when multiple options exist"
    )

    @validator('ratings')
    def validate_instrument_rating(cls, v, values):
        """Ensure IFR operations require an instrument rating."""
        if (values.get('flight_rules') == FlightRules.IFR and
            PilotRatings.INSTRUMENT not in v):
            raise ValueError('Instrument rating required for IFR operations')
        return v

    @validator('night_minimums')
    def night_mins_more_conservative(cls, v, values):
        """Ensure night minimums are at least as conservative as day minimums."""
        if v is not None:
            day = values['day_minimums']
            if (v.visibility_sm < day.visibility_sm or
                v.ceiling_ft < day.ceiling_ft):
                raise ValueError('Night minimums must be at least as conservative as day minimums')
        return v

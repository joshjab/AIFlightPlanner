"""
Contains the data models for briefing requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class NotamInfo(BaseModel):
    id: str
    text: str

class WeatherInfo(BaseModel):
    metar: str
    taf: Optional[str] = None

class RouteInfo(BaseModel):
    departure: str
    destination: str
    distance: float
    estimated_time_enroute: str

class BriefingResponse(BaseModel):
    """API response model for /api/briefing endpoint"""
    route: RouteInfo
    weather: dict[str, WeatherInfo]  # departure, destination
    notams: dict[str, List[NotamInfo]]  # departure, destination

class BriefingRequest(BaseModel):
    """API request model for /api/briefing endpoint"""
    departure: str = Field(..., min_length=4, max_length=4, description="Departure airport ICAO code")
    destination: str = Field(..., min_length=4, max_length=4, description="Destination airport ICAO code")
    pilot_preferences: Optional[dict] = Field(None, description="Optional pilot preferences for Go/No-Go")

"""
Contains the data models for briefing requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class NotamInfo(BaseModel):
    """Model for a single NOTAM with all fields from actual NOTAM data"""
    number: str
    type: str
    issued: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str
    icao_message: Optional[str] = None
    traditional_message: Optional[str] = None
    plain_language_message: Optional[str] = None
    facility: str
    icao_id: str
    airport_name: str
    keyword: str
    cancelled_or_expired: bool

class WeatherInfo(BaseModel):
    metar: str
    taf: Optional[str] = None

class RouteInfo(BaseModel):
    departure: str
    destination: str
    distance: float
    estimated_time_enroute: str

class RecommendationInfo(BaseModel):
    """Model for Go/No-Go recommendation results"""
    recommendation: bool  # True for Go, False for No-Go
    reasons: List[str]  # List of reasons supporting the recommendation

class BriefingResponse(BaseModel):
    """API response model for /api/briefing endpoint"""
    route: RouteInfo
    weather: dict[str, WeatherInfo]  # departure, destination
    notams: dict[str, List[NotamInfo]]  # departure, destination
    recommendation: Optional[RecommendationInfo] = None  # Only present if pilot preferences provided

class BriefingRequest(BaseModel):
    """API request model for /api/briefing endpoint"""
    departure: str = Field(..., min_length=4, max_length=4, description="Departure airport ICAO code")
    destination: str = Field(..., min_length=4, max_length=4, description="Destination airport ICAO code")
    pilot_preferences: Optional[dict] = Field(None, description="Optional pilot preferences for Go/No-Go")

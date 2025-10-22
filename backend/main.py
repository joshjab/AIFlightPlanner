import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from backend.scripts.populate_airport_data import populate_airport_data
from backend.models.briefing import (
    BriefingRequest, BriefingResponse, NotamInfo,
    WeatherInfo, RouteInfo, RecommendationInfo
)
from backend.models.pilot_preferences import PilotPreferences
from backend.services import recommendation_service
from backend.services.notam_service import get_notams, NotamServiceError
from backend.services.weather_service import get_weather_data, get_enroute_weather_warnings
from backend.services.airport_service import get_airport_by_icao

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    print("Application startup: Checking and populating airport data...")
    populate_airport_data()
    yield
    # Shutdown event (optional)
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/notams/{icao_code}")
def get_notams_endpoint(icao_code: str):
    try:
        notams = get_notams(icao_code)
        return notams
    except NotamServiceError as e:
        raise HTTPException(status_code=503, detail=f"NOTAM service error: {str(e)}")
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/notams/{icao_code}")
def get_notams_endpoint(icao_code: str):
    try:
        notams = get_notams(icao_code)
        return notams
    except NotamServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/briefing", response_model=BriefingResponse)
async def get_briefing(
    departure: str = Query(..., min_length=4, max_length=4, description="Departure airport ICAO code"),
    destination: str = Query(..., min_length=4, max_length=4, description="Destination airport ICAO code"),
    pilot_preferences: str = Query(None, description="Optional pilot preferences for Go/No-Go as JSON string"),
):
    """
    Get a comprehensive briefing for a flight between two airports.
    
    Args:
        departure: Departure airport ICAO code
        destination: Destination airport ICAO code
        pilot_preferences: Optional JSON string containing pilot preferences
        
    Returns:
        BriefingResponse containing weather, NOTAMs, route information, and recommendations
    
    Raises:
        HTTPException: For various error conditions including missing airports and coordinates
    """
    print(f"Processing briefing request for {departure} to {destination}")
    try:
        # Parse pilot preferences if provided
        preferences_obj = None
        if pilot_preferences:
            try:
                preferences_dict = json.loads(pilot_preferences)
                preferences_obj = PilotPreferences(**preferences_dict)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pilot preferences JSON format")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid pilot preferences: {str(e)}")
        
        print("Fetching airport details...")
        # Get departure and destination details
        dep_details = get_airport_by_icao(departure)
        dest_details = get_airport_by_icao(destination)
        
        print(f"Departure details: {dep_details}")
        print(f"Destination details: {dest_details}")
        
        if not dep_details or not dest_details:
            raise HTTPException(status_code=404, detail="Airport not found")

        # Get weather information
        dep_weather = get_weather_data(departure)
        dest_weather = get_weather_data(destination)

        # Get NOTAMs
        dep_notams = get_notams(departure)
        dest_notams = get_notams(destination)

        # Get route information and recommendation
        try:
            distance, estimated_time = recommendation_service.calculate_route_info(departure, destination)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        go_nogo, reasons = recommendation_service.get_recommendation(
            departure,
            destination,
            preferences_obj
        )

        print("Building response...")
        print(f"Weather data: dep={dep_weather}, dest={dest_weather}")
        #print(f"NOTAM data: dep={dep_notams}, dest={dest_notams}")

        # Create recommendation info if pilot preferences were provided
        recommendation_info = None
        if preferences_obj:
            recommendation_info = RecommendationInfo(
                recommendation=go_nogo,
                reasons=reasons
            )

        response = BriefingResponse(
            route=RouteInfo(
                departure=departure,
                destination=destination,
                distance=distance,
                estimated_time_enroute=estimated_time
            ),
            weather={
                "departure": WeatherInfo(**dep_weather),
                "destination": WeatherInfo(**dest_weather)
            },
            recommendation=recommendation_info,
            notams={
                "departure": [NotamInfo(
                    number=n["number"],
                    type=n["type"],
                    issued=n["issued"],
                    start_date=n.get("start_date"),
                    end_date=n.get("end_date"),
                    status=n["status"],
                    icao_message=n.get("icao_message"),
                    traditional_message=n.get("traditional_message"),
                    plain_language_message=n.get("plain_language_message"),
                    facility=n["facility"],
                    icao_id=n["icao_id"],
                    airport_name=n["airport_name"],
                    keyword=n["keyword"],
                    cancelled_or_expired=n["cancelled_or_expired"]
                ) for n in dep_notams],
                "destination": [NotamInfo(
                    number=n["number"],
                    type=n["type"],
                    issued=n["issued"],
                    start_date=n.get("start_date"),
                    end_date=n.get("end_date"),
                    status=n["status"],
                    icao_message=n.get("icao_message"),
                    traditional_message=n.get("traditional_message"),
                    plain_language_message=n.get("plain_language_message"),
                    facility=n["facility"],
                    icao_id=n["icao_id"],
                    airport_name=n["airport_name"],
                    keyword=n["keyword"],
                    cancelled_or_expired=n["cancelled_or_expired"]
                ) for n in dest_notams]
            }
        )
        #print(f"Response built: {response}")
        return response
    except NotamServiceError as e:
        raise HTTPException(status_code=503, detail=f"NOTAM service error: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
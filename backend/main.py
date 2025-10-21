from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from backend.scripts.populate_airport_data import populate_airport_data
from backend.models.briefing import (
    BriefingRequest, BriefingResponse, NotamInfo,
    WeatherInfo, RouteInfo
)
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
def get_briefing(
    departure: str = Query(..., min_length=4, max_length=4, description="Departure airport ICAO code"),
    destination: str = Query(..., min_length=4, max_length=4, description="Destination airport ICAO code"),
):
    """
    Get a comprehensive briefing for a flight between two airports.
    
    Args:
        departure: Departure airport ICAO code
        destination: Destination airport ICAO code
        
    Returns:
        BriefingResponse containing weather, NOTAMs, and route information
    """
    print(f"Processing briefing request for {departure} to {destination}")
    try:
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

        # Get distance and estimated time (basic calculation for now)
        distance = 100  # TODO: Calculate actual distance
        time = "1:00"  # TODO: Calculate actual time

        print("Building response...")
        print(f"Weather data: dep={dep_weather}, dest={dest_weather}")
        print(f"NOTAM data: dep={dep_notams}, dest={dest_notams}")

        response = BriefingResponse(
            route=RouteInfo(
                departure=departure,
                destination=destination,
                distance=distance,
                estimated_time_enroute=time
            ),
            weather={
                "departure": WeatherInfo(**dep_weather),
                "destination": WeatherInfo(**dest_weather)
            },
            notams={
                "departure": [NotamInfo(id=n["id"], text=n["text"]) for n in dep_notams],
                "destination": [NotamInfo(id=n["id"], text=n["text"]) for n in dest_notams]
            }
        )
        print(f"Response built: {response}")
        return response
    except NotamServiceError as e:
        raise HTTPException(status_code=503, detail=f"NOTAM service error: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from backend.scripts.populate_airport_data import populate_airport_data
from backend.services.notam_service import get_notams, NotamServiceError

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
        raise HTTPException(status_code=503, detail=str(e))
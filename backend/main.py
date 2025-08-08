from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.scripts.populate_airport_data import populate_airport_data

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

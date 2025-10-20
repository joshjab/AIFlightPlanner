from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add the backend directory to sys.path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from backend.database import engine
from backend.schemas import Airport

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Get total count
    total_count = session.query(Airport).count()
    print(f"Total airports in database: {total_count}")

    # Get a sample of airports
    sample = session.query(Airport).limit(5).all()
    print("\nSample airports:")
    for airport in sample:
        print(f"\nICAO: {airport.icao_code}")
        print(f"Name: {airport.name}")
        print(f"Elevation: {airport.elevation}")
        print(f"Runways: {airport.runways}")
        print(f"Last Updated: {airport.last_updated}")

except Exception as e:
    print(f"Error querying database: {e}")
finally:
    session.close()

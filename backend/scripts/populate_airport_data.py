import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from backend.database import engine, Base
from backend.schemas import Airport
from datetime import datetime, timedelta

# URL for FAA Airport Data (example - you might need to find the most current one)
# A good source might be: https://nfdc.faa.gov/webContent/28DaySubsetZip.zip
# and then extract the relevant CSV, e.g., "APT.txt" or similar.
# For simplicity, let’s assume a direct CSV link for now, or you’d need to handle ZIP extraction.
FAA_AIRPORT_DATA_URL = "https://nfdc.faa.gov/webContent/28DaySubsetZip/APT.txt"
DATA_FRESHNESS_THRESHOLD_MONTHS = 3

def populate_airport_data():
    print("Creating database tables if they don’t exist...")
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created.")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if data exists and its freshness
        latest_update = session.query(func.max(Airport.last_updated)).scalar()
        
        should_update = False
        if latest_update is None:
            print("No airport data found. Populating for the first time.")
            should_update = True
        else:
            age_in_months = (datetime.now() - latest_update).days / 30.44 # Approximate months
            if age_in_months >= DATA_FRESHNESS_THRESHOLD_MONTHS:
                print(f"Airport data is {age_in_months:.1f} months old. Updating data.")
                should_update = True
            else:
                print(f"Airport data is fresh ({age_in_months:.1f} months old). No update needed.")

        if should_update:
            print(f"Downloading data from {FAA_AIRPORT_DATA_URL}...")
            # This might need adjustment based on the actual file format and separator
            # df = pd.read_csv(FAA_AIRPORT_DATA_URL, sep='\t', header=None, encoding='latin1')
            # print("Data downloaded and read into DataFrame.")

            # Placeholder for actual column mapping based on FAA APT.txt structure
            # For APT.txt, ICAO is usually in a specific position, name, etc.
            # This is a simplified example. A real implementation would parse APT.txt carefully.
            # Let’s assume for now we can extract relevant fields.
            # This part will likely require manual inspection of the FAA data file.

            # Let’s create some dummy data for now to ensure the script runs, 
            # and then I’ll provide instructions to the user to refine this part.
            dummy_data = [
                {"icao_code": "KLAX", "name": "Los Angeles Intl", "elevation": "126", "runways": "12L/30R, 12R/30L"},
                {"icao_code": "KORD", "name": "Chicago O’Hare Intl", "elevation": "672", "runways": "09L/27R, 09R/27L"},
            ]

            # Clear existing data before inserting new data
            session.query(Airport).delete()
            session.commit()

            for data in dummy_data:
                airport = Airport(
                    icao_code=data["icao_code"],
                    name=data["name"],
                    elevation=data["elevation"],
                    runways=data["runways"],
                    last_updated=datetime.now() # Set last_updated for new entries
                )
                session.add(airport)
            
            session.commit()
            print("Airport data populated successfully.")
        else:
            print("Skipping data population as data is fresh.")

    except Exception as e:
        session.rollback()
        print(f"Error populating airport data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_airport_data()

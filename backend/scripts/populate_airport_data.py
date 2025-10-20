import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from backend.database import engine, Base
from backend.schemas import Airport
from datetime import datetime, timedelta

# URLs for ourairports-data on GitHub
AIRPORTS_CSV_URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
RUNWAYS_CSV_URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv"

DATA_FRESHNESS_THRESHOLD_MONTHS = 3

def populate_airport_data():
    """
    Downloads airport and runway data, processes it, and updates the database.
    
    Performs an "upsert":
    - If an airport (by icao_code) exists, it's updated.
    - If it doesn't exist, it's created.
    """
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
            # 1. Download data
            print(f"Downloading data from {AIRPORTS_CSV_URL}...")
            df_airports = pd.read_csv(AIRPORTS_CSV_URL)
            print(f"Downloading data from {RUNWAYS_CSV_URL}...")
            df_runways = pd.read_csv(RUNWAYS_CSV_URL)

            # 2. Process Runway Data
            # Create a 'runway_pair' (e.g., "09L/27R")
            print("Processing runway data...")
            df_runways_clean = df_runways.dropna(subset=['le_ident', 'he_ident'])
            df_runways_clean['runway_pair'] = df_runways_clean['le_ident'].astype(str) + '/' + df_runways_clean['he_ident'].astype(str)
            
            # Group by airport and aggregate runway strings
            runway_groups = df_runways_clean.groupby('airport_ident')['runway_pair'].apply(lambda x: ', '.join(x))
            df_runway_summary = runway_groups.reset_index(name='runways')

            # 3. Merge Airport and Runway Data
            print("Merging airport and runway data...")
            df_merged = pd.merge(
                df_airports, 
                df_runway_summary, 
                left_on='ident', 
                right_on='airport_ident', 
                how='left'
            )

            # 4. Select and rename columns for our schema
            df_final = df_merged[['ident', 'name', 'elevation_ft', 'latitude_deg', 'longitude_deg', 'runways']]
            df_final = df_final.rename(columns={
                'ident': 'icao_code',
                'elevation_ft': 'elevation',
                'latitude_deg': 'latitude',
                'longitude_deg': 'longitude'
            })

            # Clean NaN values, replacing them with None (which becomes NULL in DB)
            df_final = df_final.where(pd.notnull(df_final), None)
            
            # 5. Perform Database Upsert
            print("Fetching existing airports from DB for comparison...")
            existing_airports = {a.icao_code: a for a in session.query(Airport).all()}
            print(f"Found {len(existing_airports)} existing airports.")

            new_count = 0
            updated_count = 0
            update_time = datetime.now()

            print("Iterating through downloaded data for updates/inserts...")
            for row in df_final.to_dict('records'):
                icao = row['icao_code']
                if not icao:
                    continue  # Skip rows with no icao_code

                airport = existing_airports.get(icao)

                if airport:
                    # Update existing airport
                    airport.name = row['name']
                    airport.elevation = str(row['elevation']) if row['elevation'] is not None else None
                    airport.runways = row['runways']
                    airport.last_updated = update_time
                    updated_count += 1
                else:
                    # Add new airport
                    new_airport = Airport(
                        icao_code=icao,
                        name=row['name'],
                        elevation=str(row['elevation']) if row['elevation'] is not None else None,
                        runways=row['runways'],
                        last_updated=update_time
                    )
                    session.add(new_airport)
                    new_count += 1
            
            session.commit()
            print(f"Airport data population complete. Added: {new_count}, Updated: {updated_count}.")

        else:
            print("Skipping data population as data is fresh.")

    except Exception as e:
        session.rollback()
        print(f"Error populating airport data: {e}")
    finally:
        session.close()
        print("Database session closed.")

if __name__ == "__main__":
    populate_airport_data()
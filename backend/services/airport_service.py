from sqlalchemy.orm import Session
from backend.schemas import Airport
from backend.database import SessionLocal, engine, Base
from backend.scripts.populate_airport_data import populate_airport_data

def get_airport(db: Session, icao_code: str):
    """
    Get airport data from the database.
    
    Args:
        db: Database session
        icao_code: The ICAO code of the airport to retrieve
        
    Returns:
        Airport object with all details or None if not found
    """
    return db.query(Airport).filter(Airport.icao_code == icao_code).first()

def get_airport_by_icao(icao_code: str) -> dict:
    """
    Get airport information by ICAO code.
    
    Args:
        icao_code: The ICAO code of the airport
        
    Returns:
        Dictionary containing airport details or None if not found
    """
    db = SessionLocal()
    try:
        airport = get_airport(db, icao_code)
        return airport.to_dict() if airport else None
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Testing Airport Service ---")
    # Ensure database tables are created
    Base.metadata.create_all(bind=engine)

    # Populate airport data if not already populated
    populate_airport_data()

    db = SessionLocal()
    try:
        # Test with a known ICAO code, e.g., "KSFO"
        icao_code_to_test = "KSFO"
        airport = get_airport(db, icao_code_to_test)

        if airport:
            print(f"Airport found for {icao_code_to_test}: {airport.name} ({airport.icao_code})")
        else:
            print(f"No airport found for {icao_code_to_test}")

        # Test with an unknown ICAO code
        icao_code_to_test_unknown = "XXXX"
        airport_unknown = get_airport(db, icao_code_to_test_unknown)
        if airport_unknown:
            print(f"Airport found for {icao_code_to_test_unknown}: {airport_unknown.name} ({airport_unknown.icao_code})")
        else:
            print(f"No airport found for {icao_code_to_test_unknown}")

    finally:
        db.close()
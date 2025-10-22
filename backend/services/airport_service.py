from typing import List, Set, Dict, Any, Union
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

def get_runway_idents(runway_data: Union[str, List[Dict[str, Any]]]) -> Set[str]:
    """
    Extracts individual runway identifiers from the airport's runway data.

    This function can handle two formats:
    1. A single string: "04L/22R, 04R/22L, 13L/31R, 13R/31L"
    2. A list of dicts: [{'ident': '04L/22R'}, {'ident': '04R/22L'}]
    
    Args:
        runway_data: The 'runways' field from the airport dictionary.

    Returns:
        A set of all individual runway identifiers (e.g., {'04L', '22R'}).
    """
    idents = set()
    
    # --- NEW: Handle string format ---
    if isinstance(runway_data, str):
        # runway_data is "04L/22R, 04R/22L, 13L/31R, 13R/31L"
        runway_pairs = runway_data.split(',')
        for pair in runway_pairs:
            # pair is "04L/22R"
            parts = pair.split('/')
            for part in parts:
                part = part.strip()
                if part:
                    idents.add(part)

    # --- Original logic for list of dicts ---
    elif isinstance(runway_data, list):
        for rwy in runway_data:
            if not isinstance(rwy, dict):
                continue  # Skip invalid entries
                
            # We assume the identifier key is 'ident'.
            name = rwy.get('ident') 
            if not name or not isinstance(name, str):
                continue
            
            # Split '09L/27R' into ['09L', '27R']
            parts = name.split('/')
            for part in parts:
                part = part.strip()
                if part:
                    idents.add(part)
            
    # For KJFK, this will now correctly return:
    # {'04L', '22R', '04R', '22L', '13L', '31R', '13R', '31L'}
    return idents

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
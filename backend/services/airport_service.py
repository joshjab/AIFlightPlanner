from sqlalchemy.orm import Session
from backend.schemas import Airport

def get_airport(db: Session, icao_code: str):
    return db.query(Airport).filter(Airport.icao_code == icao_code).first()

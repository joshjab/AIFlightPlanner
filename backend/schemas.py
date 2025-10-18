from sqlalchemy import Column, Integer, String, DateTime, func
from backend.database import Base

class Airport(Base):
    __tablename__ = "airports"

    icao_code = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    elevation = Column(String)
    runways = Column(String) # Storing as string for simplicity, can be more complex object
    metar = Column(String, nullable=True)
    taf = Column(String, nullable=True)
    notams = Column(String, nullable=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

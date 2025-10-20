from sqlalchemy import Column, Integer, String, DateTime, Float, func
from backend.database import Base

class Airport(Base):
    __tablename__ = "airports"

    icao_code = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    elevation = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    runways = Column(String)  # JSON string of runway info
    metar = Column(String, nullable=True)
    taf = Column(String, nullable=True)
    notams = Column(String, nullable=True)  # JSON string of NOTAM list
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert airport object to dictionary"""
        return {
            "icao": self.icao_code,
            "name": self.name,
            "elevation": self.elevation,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "runways": self.runways,
            "metar": self.metar,
            "taf": self.taf,
            "notams": self.notams,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

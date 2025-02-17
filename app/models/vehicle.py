from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    mileage = Column(Float)
    price = Column(Float)
    monthly_rental_price = Column(Float)
    is_available_for_sale = Column(Boolean, default=True)
    is_available_for_rent = Column(Boolean, default=False)
    features = Column(JSON)
    images = Column(JSON)
    technical_details = Column(JSON)
    
    rentals = relationship("Rental", back_populates="vehicle")
    dossiers = relationship("Dossier", back_populates="vehicle")
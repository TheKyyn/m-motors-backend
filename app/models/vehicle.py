from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Boolean, JSON, DateTime, Enum, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..database import Base

class FuelType(str, PyEnum):
    ESSENCE = "essence"
    DIESEL = "diesel"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"

class TransmissionType(str, PyEnum):
    MANUELLE = "manuelle"
    AUTOMATIQUE = "automatique"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    # Identifiant
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    mileage = Column(Float)
    registration_number: Mapped[str] = mapped_column(String(20), unique=True)
    
    # Prix et disponibilité
    price = Column(Float)
    monthly_rental_price: Mapped[float] = mapped_column(Float)
    is_available_for_sale: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available_for_rent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Caractéristiques techniques
    fuel_type = Column(Enum(FuelType))
    transmission = Column(Enum(TransmissionType))
    engine_size: Mapped[float] = mapped_column(Float)  # en litres
    power = Column(Integer)  # Puissance en chevaux
    doors = Column(Integer)
    seats = Column(Integer)
    
    # Détails supplémentaires
    color = Column(String)
    features: Mapped[dict] = mapped_column(JSON)  # équipements
    images: Mapped[List[str]] = mapped_column(JSON)  # URLs des images
    technical_details: Mapped[dict] = mapped_column(JSON)
    
    # Maintenance
    last_maintenance_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_maintenance_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relations
    rentals: Mapped[list["Rental"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )
    dossiers: Mapped[list["Dossier"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "mileage": self.mileage,
            "price": self.price,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "power": self.power,
            "doors": self.doors,
            "seats": self.seats,
            "color": self.color,
            "is_available_for_sale": self.is_available_for_sale,
            "is_available_for_rent": self.is_available_for_rent,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
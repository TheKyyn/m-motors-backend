from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Boolean, JSON, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from .database import Base

class FuelType(PyEnum):
    ESSENCE = "essence"
    DIESEL = "diesel"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"

class TransmissionType(PyEnum):
    MANUELLE = "manuelle"
    AUTOMATIQUE = "automatique"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    # Identifiant
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Informations de base
    brand: Mapped[str] = mapped_column(String(100), index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)
    year: Mapped[int]
    mileage: Mapped[float] = mapped_column(Float)
    registration_number: Mapped[str] = mapped_column(String(20), unique=True)
    
    # Prix et disponibilité
    price: Mapped[float] = mapped_column(Float)
    monthly_rental_price: Mapped[float] = mapped_column(Float)
    is_available_for_sale: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available_for_rent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Caractéristiques techniques
    fuel_type: Mapped[FuelType] = mapped_column(Enum(FuelType))
    transmission: Mapped[TransmissionType] = mapped_column(Enum(TransmissionType))
    engine_size: Mapped[float] = mapped_column(Float)  # en litres
    power: Mapped[int]  # en chevaux
    doors: Mapped[int]
    seats: Mapped[int]
    
    # Détails supplémentaires
    color: Mapped[str] = mapped_column(String(50))
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
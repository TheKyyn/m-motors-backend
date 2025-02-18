from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class FuelType(str, Enum):
    ESSENCE = "essence"
    DIESEL = "diesel"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"

class TransmissionType(str, Enum):
    MANUELLE = "manuelle"
    AUTOMATIQUE = "automatique"

class VehicleBase(BaseModel):
    """Schéma de base pour les véhicules"""
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    mileage: float = Field(..., ge=0)
    registration_number: str = Field(..., pattern=r'^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$')
    price: float = Field(..., gt=0)
    monthly_rental_price: float = Field(..., gt=0)
    is_available_for_sale: bool = True
    is_available_for_rent: bool = False
    fuel_type: FuelType
    transmission: TransmissionType
    engine_size: float = Field(..., gt=0)
    power: int = Field(..., gt=0)
    doors: int = Field(..., ge=2, le=7)
    seats: int = Field(..., ge=2, le=9)
    color: str = Field(..., min_length=1, max_length=50)
    features: Dict[str, bool] = Field(default_factory=dict)
    images: List[str] = Field(default_factory=list)
    technical_details: Dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class VehicleCreate(VehicleBase):
    """Schéma pour la création d'un véhicule"""
    pass

class VehicleUpdate(BaseModel):
    """Schéma pour la mise à jour d'un véhicule"""
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    mileage: Optional[float] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)
    monthly_rental_price: Optional[float] = Field(None, gt=0)
    is_available_for_sale: Optional[bool] = None
    is_available_for_rent: Optional[bool] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    engine_size: Optional[float] = Field(None, gt=0)
    power: Optional[int] = Field(None, gt=0)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    features: Optional[Dict[str, bool]] = None
    images: Optional[List[str]] = None
    technical_details: Optional[Dict[str, str]] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class VehicleInDB(VehicleBase):
    """Schéma pour un véhicule en base de données"""
    id: int
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class VehicleResponse(VehicleInDB):
    """Schéma pour la réponse API"""
    pass

class VehicleFilter(BaseModel):
    """Schéma pour le filtrage des véhicules"""
    brand: Optional[str] = None
    model: Optional[str] = None
    min_year: Optional[int] = Field(None, ge=1900)
    max_year: Optional[int] = Field(None, le=datetime.now().year + 1)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    available_for_sale: Optional[bool] = None
    available_for_rent: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel
from typing import Optional, List, Dict

class VehicleBase(BaseModel):
    brand: str
    model: str
    year: int
    mileage: float
    price: float
    monthly_rental_price: Optional[float]
    is_available_for_sale: bool = True
    is_available_for_rent: bool = False
    features: Optional[Dict] = {}
    images: Optional[List[str]] = []
    technical_details: Optional[Dict] = {}

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: int

    class Config:
        orm_mode = True

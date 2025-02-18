from pydantic import BaseModel, Field
from typing import Optional

class RentalOptionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    monthly_price: float = Field(..., gt=0)
    is_mandatory: bool = False

class RentalOptionCreate(RentalOptionBase):
    pass

class RentalOptionResponse(RentalOptionBase):
    id: int

    class Config:
        from_attributes = True 
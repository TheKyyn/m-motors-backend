from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from ..database import Base
from ..schemas.rental_services import ServiceType, ServiceStatus

class RentalService(Base):
    __tablename__ = "rental_services"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ServiceType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price_per_month = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=False)
    terms_and_conditions = Column(String, nullable=False)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIF)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "price_per_month": self.price_per_month,
            "duration_months": self.duration_months,
            "is_mandatory": self.is_mandatory,
            "terms_and_conditions": self.terms_and_conditions,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from ..database import Base

class RentalStatus(str, PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_price = Column(Float)
    status = Column(Enum(RentalStatus), default=RentalStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="rentals")
    vehicle = relationship("Vehicle", back_populates="rentals")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 
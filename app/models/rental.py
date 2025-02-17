from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    monthly_price = Column(Float)
    insurance_included = Column(Boolean, default=False)
    maintenance_included = Column(Boolean, default=False)
    assistance_included = Column(Boolean, default=False)
    technical_control_included = Column(Boolean, default=False)
    status = Column(String, default="pending")

    vehicle = relationship("Vehicle", back_populates="rentals")
    user = relationship("User", back_populates="rentals") 
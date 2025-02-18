from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class RentalOption(Base):
    __tablename__ = "rental_options"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    monthly_price = Column(Float, nullable=False)
    is_mandatory = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "monthly_price": self.monthly_price,
            "is_mandatory": self.is_mandatory
        } 
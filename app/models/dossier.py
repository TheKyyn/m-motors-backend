from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Dossier(Base):
    __tablename__ = "dossiers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    status = Column(String, default="pending")
    is_purchase = Column(Boolean, default=True)
    documents_url = Column(String)

    user = relationship("User", back_populates="dossiers")
    vehicle = relationship("Vehicle", back_populates="dossiers")
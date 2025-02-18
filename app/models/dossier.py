from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from .dossier_rental_option import dossier_rental_options

from ..database import Base

class DossierType(str, PyEnum):
    """Type de dossier"""
    ACHAT = "ACHAT"
    LOCATION = "LOCATION"

class DossierStatus(str, PyEnum):
    """Statut du dossier"""
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS_DE_TRAITEMENT = "EN_COURS_DE_TRAITEMENT"
    DOCUMENTS_MANQUANTS = "DOCUMENTS_MANQUANTS"
    ACCEPTE = "ACCEPTE"
    REFUSE = "REFUSE"
    ANNULE = "ANNULE"

def utcnow():
    """Retourne la date et l'heure actuelles en UTC"""
    return datetime.now(timezone.utc)

class Dossier(Base):
    __tablename__ = "dossiers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    
    # Type et statut
    type = Column(Enum(DossierType), nullable=False)
    status = Column(Enum(DossierStatus), default=DossierStatus.EN_ATTENTE)
    
    # Informations financières
    monthly_income = Column(Float, nullable=False)
    employment_contract_type = Column(String, nullable=False)
    employer_name = Column(String, nullable=False)
    employment_start_date = Column(DateTime(timezone=True), nullable=False)
    current_loans_monthly_payments = Column(Float, default=0)
    
    # Documents et commentaires
    documents = Column(JSONB, server_default='[]')
    comments = Column(String, nullable=True)
    admin_comments = Column(String, nullable=True)
    
    # Pour les locations
    desired_loan_duration = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relations
    user = relationship("User", back_populates="dossiers")
    vehicle = relationship("Vehicle", back_populates="dossiers")
    rental_options = relationship(
        "RentalOption",
        secondary=dossier_rental_options,
        backref="dossiers"
    )

    def to_dict(self):
        base_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "monthly_income": self.monthly_income,
            "employment_contract_type": self.employment_contract_type,
            "employer_name": self.employer_name,
            "employment_start_date": self.employment_start_date,
            "current_loans_monthly_payments": self.current_loans_monthly_payments,
            "documents": self.documents or [],
            "comments": self.comments,
            "admin_comments": self.admin_comments,
            "desired_loan_duration": self.desired_loan_duration,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        base_dict["rental_options"] = [option.to_dict() for option in self.rental_options]
        return base_dict
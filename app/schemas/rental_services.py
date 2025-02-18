from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ServiceType(str, Enum):
    """Type de service"""
    ASSURANCE = "ASSURANCE"
    ASSISTANCE = "ASSISTANCE"
    ENTRETIEN = "ENTRETIEN"
    CONTROLE_TECHNIQUE = "CONTROLE_TECHNIQUE"

class ServiceStatus(str, Enum):
    """Statut du service"""
    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    EN_ATTENTE = "EN_ATTENTE"
    EXPIRE = "EXPIRE"

class ServiceBase(BaseModel):
    """Schéma de base pour les services"""
    type: ServiceType
    name: str = Field(..., min_length=2, max_length=100)
    description: str
    price_per_month: float = Field(..., gt=0)
    duration_months: int = Field(..., ge=1, le=60)
    is_mandatory: bool = False
    terms_and_conditions: str

class ServiceCreate(ServiceBase):
    """Schéma pour la création d'un service"""
    pass

class ServiceUpdate(BaseModel):
    """Schéma pour la mise à jour d'un service"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price_per_month: Optional[float] = Field(None, gt=0)
    duration_months: Optional[int] = Field(None, ge=1, le=60)
    is_mandatory: Optional[bool] = None
    terms_and_conditions: Optional[str] = None
    status: Optional[ServiceStatus] = None

class ServiceInDB(ServiceBase):
    """Schéma pour un service en base de données"""
    id: int
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime

class ServiceResponse(ServiceInDB):
    """Schéma pour la réponse API"""
    pass

class ServiceFilter(BaseModel):
    """Schéma pour le filtrage des services"""
    type: Optional[ServiceType] = None
    status: Optional[ServiceStatus] = None
    is_mandatory: Optional[bool] = None
    max_price_per_month: Optional[float] = None 
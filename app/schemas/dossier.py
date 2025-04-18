from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

class DossierType(str, Enum):
    """Type de dossier"""
    ACHAT = "ACHAT"
    LOCATION = "LOCATION"

class DossierStatus(str, Enum):
    """Statut du dossier"""
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS_DE_TRAITEMENT = "EN_COURS_DE_TRAITEMENT"
    DOCUMENTS_MANQUANTS = "DOCUMENTS_MANQUANTS"
    ACCEPTE = "ACCEPTE"
    REFUSE = "REFUSE"
    ANNULE = "ANNULE"

class Document(BaseModel):
    """Schéma pour un document"""
    name: str
    type: str
    url: str
    uploaded_at: datetime
    status: str = "en_attente"
    comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DossierBase(BaseModel):
    """Schéma de base pour les dossiers"""
    type: DossierType
    vehicle_id: int
    monthly_income: float = Field(..., gt=0)
    employment_contract_type: str = Field(..., min_length=2, max_length=50)
    employer_name: str = Field(..., min_length=2, max_length=100)
    employment_start_date: datetime
    current_loans_monthly_payments: float = Field(default=0, ge=0)
    comments: Optional[str] = None
    desired_loan_duration: Optional[int] = Field(None, ge=12, le=84)  # en mois

    model_config = ConfigDict(from_attributes=True)

class DossierCreate(DossierBase):
    """Schéma pour la création d'un dossier"""
    pass

class DossierUpdate(BaseModel):
    """Schéma pour la mise à jour d'un dossier"""
    monthly_income: Optional[float] = Field(None, gt=0)
    employment_contract_type: Optional[str] = Field(None, min_length=2, max_length=50)
    employer_name: Optional[str] = Field(None, min_length=2, max_length=100)
    employment_start_date: Optional[datetime] = None
    current_loans_monthly_payments: Optional[float] = Field(None, ge=0)
    comments: Optional[str] = None
    status: Optional[DossierStatus] = None
    admin_comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DossierInDB(DossierBase):
    """Schéma pour un dossier en base de données"""
    id: int
    user_id: int
    status: DossierStatus = DossierStatus.EN_ATTENTE
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    admin_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('documents', mode='before')
    @classmethod
    def ensure_documents_list(cls, v: Any) -> List[Dict[str, Any]]:
        """Assure que les documents sont toujours une liste"""
        if v is None:
            return []
        if isinstance(v, dict) and not v:
            return []
        if isinstance(v, list):
            return v
        raise ValueError("Le champ documents doit être une liste")

class DossierResponse(DossierInDB):
    """Schéma pour la réponse API"""
    pass

class DossierFilter(BaseModel):
    """Schéma pour le filtrage des dossiers"""
    type: Optional[DossierType] = None
    status: Optional[DossierStatus] = None
    vehicle_id: Optional[int] = None
    user_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

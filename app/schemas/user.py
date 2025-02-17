from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = Field(None, pattern=r'^[0-9]{5}$')
    country: str = "France"
    is_admin: bool = False

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    # Au moins 8 caractères, au moins une lettre et un chiffre
    password: str = Field(..., min_length=8, pattern=r'[A-Za-z0-9]{8,}')

class UserUpdate(UserBase):
    """Schéma pour la mise à jour d'un utilisateur"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8, pattern=r'[A-Za-z0-9]{8,}')

class UserInDB(UserBase):
    """Schéma pour un utilisateur en base de données"""
    id: int
    phone_number: Optional[str] = None  # Changé de phone à phone_number
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDB):
    """Schéma pour la réponse API"""
    pass

class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schéma pour les données du token"""
    email: str
    is_admin: bool

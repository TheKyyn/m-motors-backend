from pydantic_settings import BaseSettings
from pydantic import EmailStr, SecretStr
from typing import Optional

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str
    
    # Sécurité
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None
    AWS_REGION: str = "eu-west-3"
    
    # S3 Configuration
    S3_BUCKET_NAME: str
    S3_VEHICLES_PREFIX: str = "vehicles/"
    S3_DOCUMENTS_PREFIX: str = "documents/"
    CLOUDFRONT_DOMAIN: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    
    # OpenAI pour le RAG Chat
    OPENAI_API_KEY: Optional[SecretStr] = None
    
    # Application
    APP_NAME: str = "M-Motors API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
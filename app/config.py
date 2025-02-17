from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/motors_db"
    secret_key: str = "supersecretkey"

settings = Settings()
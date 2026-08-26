import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ControlPlane.ai"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./controlplane.db"
    
    # Cryptography & Security
    CONTROLPLANE_TOKEN_SECRET: str = "controlplane_super_secret_hmac_key_change_in_production_2026"
    TOKEN_TTL_SECONDS: int = 300
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Provider
    DEMO_MODE: bool = True
    AI_PROVIDER: str = "mock"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

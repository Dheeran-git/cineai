import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "SmartCut AI")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smartcut")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")

    class Config:
        case_sensitive = True

settings = Settings()

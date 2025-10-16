import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/requirement_test_db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    class Config:
        env_file = ".env"

settings = Settings()
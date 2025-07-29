from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    DATABASE_POOL_SIZE: int = 10

    # Security
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    COOKIE_SECURE: bool = False  # True in prod (HTTPS)
    COOKIE_SAMESITE: str = "lax"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    UPLOAD_DIR: str = "/uploads"

    ENVIRONMENT: str = "development"  # "production" or "development"
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()

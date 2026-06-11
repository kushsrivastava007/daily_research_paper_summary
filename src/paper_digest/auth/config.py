# src/paper_digest/auth/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """OAuth and app settings from environment variables."""

    # OAuth - Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/auth/callback/google"
    )

    # OAuth - GitHub
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI: str = os.getenv(
        "GITHUB_REDIRECT_URI",
        "http://localhost:8000/auth/callback/github"
    )

    # App settings
    APP_NAME: str = "Paper Digest"
    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv(
        "SENDGRID_FROM_EMAIL",
        "noreply@paperdigest.ai"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

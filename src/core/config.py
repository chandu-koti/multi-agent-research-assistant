import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings configuration using Pydantic Settings.
    Loads settings hierarchy: Environment Variables -> .env file -> Default values.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # FastAPI Metadata
    APP_NAME: str = "Multi-Agent AI Research Assistant"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # API Credentials (Placeholders for downstream steps)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    TAVILY_API_KEY: str | None = None

# Initialize settings singleton
settings = Settings()

"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Required configuration
    openai_api_key: str
    model_name: str
    vector_db_path: str
    debug: bool = False
    
    # Optional application settings
    app_name: str = "FinPol"
    host: str = "0.0.0.0"
    port: int = 8000
    risk_threshold_high: int = 80
    risk_threshold_medium: int = 50


@lru_cache
def get_settings() -> Settings:
    """Get singleton settings instance."""
    return Settings()


# Singleton settings object
settings = get_settings()

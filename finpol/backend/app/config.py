"""Application configuration with Pydantic BaseSettings."""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Required configuration
    openai_api_key: str = Field(..., description="OpenAI API key for LLM")
    model_name: str = Field(default="gpt-4", description="LLM model name")
    vector_db_path: str = Field(default="./data/faiss_index", description="Path to FAISS vector database")
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # Optional application settings
    app_name: str = Field(default="FinPol", description="Application name")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    risk_threshold_high: int = Field(default=80, ge=0, le=100, description="High risk threshold")
    risk_threshold_medium: int = Field(default=50, ge=0, le=100, description="Medium risk threshold")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    api_version: str = Field(default="1.0.0", description="API version")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    
    # Database
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        """Validate OpenAI API key is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("OPENAI_API_KEY cannot be empty")
        if v.startswith("sk-"):
            return v
        raise ValueError("OPENAI_API_KEY must start with 'sk-'")
    
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name."""
        allowed_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        if v not in allowed_models:
            raise ValueError(f"MODEL_NAME must be one of: {allowed_models}")
        return v
    
    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins."""
        if not v:
            return ["*"]
        return v
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


@lru_cache
def get_settings() -> Settings:
    """Get singleton settings instance."""
    return Settings()


# Singleton settings object
settings = get_settings()

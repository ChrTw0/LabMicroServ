"""
Service configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    """Settings for billing-service"""

    # Service info
    service_name: str = Field(default="billing-service", env="SERVICE_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default=8005, env="PORT")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_echo: bool = Field(default=False, env="DB_ECHO")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Service URLs
    order_service_url: str = Field(default="http://localhost:8004", env="ORDER_SERVICE_URL")
    patient_service_url: str = Field(default="http://localhost:8002", env="PATIENT_SERVICE_URL")
    configuration_service_url: str = Field(default="http://localhost:8010", env="CONFIGURATION_SERVICE_URL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

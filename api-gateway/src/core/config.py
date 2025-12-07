"""
API Gateway configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Settings for api-gateway"""

    # Service info
    service_name: str = Field(default="api-gateway", env="SERVICE_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default=8000, env="PORT")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:8000",
            "http://localhost:5173"  # Vite dev server
        ],
        env="CORS_ORIGINS"
    )

    # Service URLs
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    patient_service_url: str = Field(default="http://localhost:8002", env="PATIENT_SERVICE_URL")
    order_service_url: str = Field(default="http://localhost:8003", env="ORDER_SERVICE_URL")
    billing_service_url: str = Field(default="http://localhost:8004", env="BILLING_SERVICE_URL")
    configuration_service_url: str = Field(default="http://localhost:8005", env="CONFIGURATION_SERVICE_URL")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton
settings = Settings()

"""
Service configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    """Settings for configuration-service"""

    # Service info
    service_name: str = Field(default="configuration-service", env="SERVICE_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default=8010, env="PORT")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_echo: bool = Field(default=False, env="DB_ECHO")

    # Security
    secret_key: str = Field(default="default-secret", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Service URLs
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")

    # MinIO Storage
    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="backups", env="MINIO_BUCKET")

    # External Services (Notifications)
    smtp_host: Optional[str] = Field(None, env="SMTP_HOST")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="", env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Laboratorio Clínico", env="SMTP_FROM_NAME")
    whatsapp_api_token: Optional[str] = Field(None, env="WHATSAPP_API_TOKEN")
    whatsapp_api_url: str = Field(default="", env="WHATSAPP_API_URL")
    whatsapp_business_number: str = Field(default="", env="WHATSAPP_BUSINESS_NUMBER")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

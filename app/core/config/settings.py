from typing import Optional
from pydantic import MongoDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    debug: bool = False
    log_full_traceback: bool = False

    # Database configuration - all optional for stateless microservices
    # TODO add PostgresDsn and @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    database_uri: Optional[str] = "sqlite+aiosqlite:///./app.db"
    db_type: Optional[str] = "sqlalchemy"  # Options: "sqlalchemy", "motor", "none", or None

    # MongoDB specific settings
    mongo_dsn: Optional[MongoDsn] = "mongodb://localhost:27017"  # type: ignore
    mongo_db_name: Optional[str] = "racun"

    # JWT Authentication settings
    jwt_secret_key: str = "for production can generate by: openssl rand -hex 64"
    jwt_algorithm: str = "HS256"
    jwt_dev_mode: bool = False  # Skip signature validation in development

    # Metrics configuration
    metrics_enabled: bool = True
    metrics_log_slow_requests: bool = True
    metrics_slow_threshold_ms: int = 1000
    metrics_include_user_agent: bool = False
    metrics_include_client_ip: bool = True

    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # API settings
    api_title: str = "FastAPI Template"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready FastAPI template"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env files."""

    app_name: str = "Customer Churn MLOps System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg://churn_user:churn_password@postgres:5432/churn_db",
        validation_alias="DATABASE_URL",
    )
    mlflow_tracking_uri: str = Field(
        default="http://mlflow:5000",
        validation_alias="MLFLOW_TRACKING_URI",
    )
    mlflow_experiment_name: str = "customer_churn_experiments"
    model_name: str = "customer_churn_random_forest"
    model_storage_dir: Path = BACKEND_DIR / "app" / "ml" / "model_storage"
    allow_auto_train: bool = True
    training_rows: int = 2500
    training_random_state: int = 42

    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

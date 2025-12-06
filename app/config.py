import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "EOTechChallenge"
    VERSION: str = "0.1.0"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    ASYNC_DATABASE_URL: str = os.getenv(
        "ASYNC_DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'eo_tech_challenge_async.db'}"
    )

    ASYNC_SQLALCHEMY_ENGINE_OPTIONS: dict = (
        {"connect_args": {"check_same_thread": False}}
        if ASYNC_DATABASE_URL.startswith("sqlite")
        else {}
    )

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()

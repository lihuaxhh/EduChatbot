# app/core/config.py
import os
import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = str(pathlib.Path(__file__).resolve().parents[2] / ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    database_url: str
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    db_init_mode: str = os.getenv("DB_INIT_MODE", "create")

settings = Settings()

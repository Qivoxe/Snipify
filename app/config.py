from fastapi import FastAPI
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Snipify"
    version: str = "0.1.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./snipify.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "development-secret-key"
    APP_ENV: str = "development"


    class config:
        env_file = ".env"

settings = Settings()
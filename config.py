import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite:///store_bot.db"
    ADMIN_IDS: list[int] = []
    DEFAULT_LANGUAGE: str = "en"
    
    class Config:
        env_file = ".env"


settings = Settings()

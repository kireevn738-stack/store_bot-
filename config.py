import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(','))) if os.getenv("ADMIN_IDS") else []

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///store_bot.db")

# Supported languages
LANGUAGES = {
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

DEFAULT_LANGUAGE = 'ru'

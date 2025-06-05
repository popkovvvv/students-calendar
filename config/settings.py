import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.environ.get('ADMIN_IDS', '')
ADMIN_IDS = set(map(int, ADMIN_IDS_STR.split(','))) if ADMIN_IDS_STR else set()

# Настройки базы данных
DATABASE_URL = "sqlite+aiosqlite:///storage/bot.db"

# Настройки Google Calendar API
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/")
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Настройки кэширования
CACHE_TTL = 10  # в секундах 

# Language settings
LANGUAGES = {
    'ru': 'Русский',
    'en': 'English'
}
DEFAULT_LANGUAGE = 'ru'
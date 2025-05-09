from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_ОТ_BOTFATHER")

POSTGRES = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("PORT_BD_POSTGRES", "5432")),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "secret"),
    "database": os.getenv("POSTGRES_DB", "fitness_bot_db")
}


DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES['user']}:{POSTGRES['password']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['database']}"
)
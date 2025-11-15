# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #DATABASE_URL: str = "postgresql://restaurant_ihc_db_user:AEzpljq81VeCsb6bemjm561CqxcrWDFf@dpg-d4bg0h3uibrs739s4a0g-a.oregon-postgres.render.com/restaurant_ihc_db"
    #DATABASE_URL: str
    DATABASE_URL: str = "postgresql://postgres:2170@localhost:5432/pedidos_bot"
    TELEGRAM_BOT_TOKEN : str 

    class Config:
        env_file = ".env"

settings = Settings()
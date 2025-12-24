from sqlalchemy import create_engine
from app.config.settings import settings

DB_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(DB_URL, pool_pre_ping=True)

def get_connection():
    return engine.connect()

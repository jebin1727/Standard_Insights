from sqlalchemy import create_engine
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT

DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL, pool_pre_ping=True)

def get_connection():
    return engine.connect()

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "your_db_host")
    DB_USER: str = os.getenv("DB_USER", "your_db_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "your_db_password")
    DB_NAME: str = os.getenv("DB_NAME", "your_db_name")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    TABLE_MAPPING: Dict[str, str] = {
        "Sales": "data_so_summary",
        "Orders": "data_so_summary",
        "Customers": "data_company_info",
        "SKUs": "data_prod_variant",
        "OrderDetails": "data_so_details"
    }
    
    ALLOWED_TABLES: List[str] = list(TABLE_MAPPING.values())
    
    
settings = Settings()

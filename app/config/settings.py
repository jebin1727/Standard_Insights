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
    
    # Common column name patterns that might exist in the database
    COMMON_COLUMN_PATTERNS = {
        "date_columns": ["created", "created_at", "date", "order_date", "so_date", "sos_date", "transaction_date", "updated", "updated_at"],
        "id_columns": ["id", "_id", "pk", "so_id", "sos_id", "order_id", "client_id", "dci_id", "customer_id", "product_id", "sku_id"],
        "amount_columns": ["total", "total_amount", "amount", "price", "cost", "value", "revenue", "sum", "quantity"]
    }
    
    ALLOWED_TABLES: List[str] = list(TABLE_MAPPING.values())
    
    
settings = Settings()

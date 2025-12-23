import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "your_db_host")
DB_USER = os.getenv("DB_USER", "your_db_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
DB_NAME = os.getenv("DB_NAME", "your_db_name")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TABLE_MAPPING = {
    "Sales": "data_so_summary",
    "Orders": "data_so_summary",
    "Customers": "data_company_info",
    "SKUs": "data_prod_variant",
    "OrderDetails": "data_so_details"
}

ALLOWED_TABLES = list(TABLE_MAPPING.values())

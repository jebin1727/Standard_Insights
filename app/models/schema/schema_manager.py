from sqlalchemy import text
from app.models.database.connection import engine
from app.config.settings import settings
from app.utils.logger import app_logger

def fetch_schema():
    app_logger.info("Fetching database schema...")
    schema_info = {}
    table_placeholders = ", ".join([f"'{t}'" for t in settings.ALLOWED_TABLES])
    query = text(f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME IN ({table_placeholders})
    """)
        
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"db_name": settings.DB_NAME})
            for row in result:
                table = row[0]
                col = row[1]
                dtype = row[2]
                comment = row[3] or ""
                
                if table not in schema_info:
                    schema_info[table] = []
                
                schema_info[table].append(f"{col} ({dtype}) {comment}".strip())
                
        # Format into snippets
        snippets = []
        for table, cols in schema_info.items():
            snippet = f"Table: {table}\nColumns:\n" + "\n".join([f"  - {c}" for c in cols])
            snippets.append({
                "table_name": table,
                "content": snippet
            })
        
        app_logger.info(f"Schema fetched successfully for {len(snippets)} tables")
        return snippets
    except Exception as e:
        app_logger.error(f"Error fetching schema: {str(e)}")
        raise

if __name__ == "__main__":
    snippets = fetch_schema()
    for s in snippets:
        print(s['content'])
        print("-" * 20)

from sqlalchemy import text
from app.models.database.connection import engine
from app.config.settings import settings
from app.utils.logger import app_logger

def fetch_schema():
    app_logger.info("Fetching database schema...")
    schema_info = {}
    table_placeholders = ", ".join([f"'{t}'" for t in settings.ALLOWED_TABLES])
    query = text(f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME IN ({table_placeholders})
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"db_name": settings.DB_NAME})
            for row in result:
                table = row[0]
                col = row[1]
                dtype = row[2]
                comment = row[3] or ""
                nullable = row[4]
                
                if table not in schema_info:
                    schema_info[table] = []
                
                col_info = f"{col} ({dtype}, {'nullable' if nullable == 'YES' else 'not null'}) {comment}".strip()
                schema_info[table].append(col_info)
                
        # Also fetch primary and foreign key information
        pk_query = text(f"""
            SELECT 
                k.TABLE_NAME,
                k.COLUMN_NAME,
                k.CONSTRAINT_NAME,
                t.CONSTRAINT_TYPE
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
            JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
                ON k.CONSTRAINT_NAME = t.CONSTRAINT_NAME
                AND k.TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE k.TABLE_SCHEMA = :db_name
                AND t.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'FOREIGN KEY')
                AND k.TABLE_NAME IN ({table_placeholders})
            ORDER BY k.TABLE_NAME, k.ORDINAL_POSITION
        """)
        
        with engine.connect() as conn:
            pk_result = conn.execute(pk_query, {"db_name": settings.DB_NAME})
            for row in pk_result:
                table = row[0]
                col = row[1]
                constraint_name = row[2]
                constraint_type = row[3]
                
                if table in schema_info:
                    # Add PK/FK information to the appropriate column
                    for i, col_info in enumerate(schema_info[table]):
                        if col_info.startswith(f"{col} "):
                            # Check if constraint info is already added to avoid duplicates
                            if f", {constraint_type.lower()}" not in col_info:
                                schema_info[table][i] = f"{col_info}, {constraint_type.lower()}"
        
        # Format into detailed snippets with better structure for LLM
        snippets = []
        for table, cols in schema_info.items():
            # Create a more structured format that clearly lists all column names
            column_list = "\n".join([f"  - {c.split(' ')[0]}" for c in cols])  # Just the column name
            detailed_info = "\n".join([f"  - {c}" for c in cols])  # Full column info
            
            snippet = f"Table: {table}\n\nAll Column Names:\n{column_list}\n\nDetailed Column Information:\n{detailed_info}\n"
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

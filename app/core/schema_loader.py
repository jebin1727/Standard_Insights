from sqlalchemy import text
from app.core.db import engine
from app.core.config import DB_NAME, ALLOWED_TABLES

def fetch_schema():
    schema_info = {}
    table_placeholders = ", ".join([f"'{t}'" for t in ALLOWED_TABLES])
    query = text(f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME IN ({table_placeholders})
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"db_name": DB_NAME})
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
    return snippets

if __name__ == "__main__":
    snippets = fetch_schema()
    for s in snippets:
        print(s['content'])
        print("-" * 20)

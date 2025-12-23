from sqlalchemy import text
from app.core.db import engine

def execute_query(sql, timeout=30, limit=100):
    # Ensure limit is applied if not already there (optional but safe)
    # Most generated queries will have their own limits if requested
    
    with engine.connect() as conn:
        # Some DB drivers support execution options for timeout
        # For mysql-connector, we rely on the DB user being read-only as primary defense
        result = conn.execute(text(sql))
        
        # Fetch rows up to limit
        rows = result.fetchmany(limit)
        
        # Convert to list of dicts
        keys = result.keys()
        data = [dict(zip(keys, row)) for row in rows]
        
        # If single result, return value, else return data
        if len(data) == 1 and len(keys) == 1:
            return list(data[0].values())[0]
            
        return data

from sqlalchemy import text
from app.models.database.connection import engine
from app.utils.logger import app_logger

def execute_query(sql, timeout=30, limit=100):
    app_logger.info(f"Executing SQL query: {sql[:100]}...")
    # Ensure limit is applied if not already there (optional but safe)
    # Most generated queries will have their own limits if requested
    
    try:
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
                result_value = list(data[0].values())[0]
                app_logger.info(f"Query executed successfully, returned single value: {result_value}")
                return result_value
                
            app_logger.info(f"Query executed successfully, returned {len(data)} rows")
            return data
    except Exception as e:
        app_logger.error(f"Error executing query '{sql[:100]}...': {str(e)}")
        raise

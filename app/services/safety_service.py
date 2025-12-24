import sqlglot
from sqlglot import exp
from app.config.settings import settings
from app.utils.logger import app_logger

BANNED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE"
]

RISKY_FUNCTIONS = [
    "SLEEP", "BENCHMARK", "LOAD_FILE", "INTO OUTFILE", "INTO DUMPFILE"
]

def validate_sql(sql: str):
    app_logger.info(f"Validating SQL: {sql[:100]}...")
    if not sql or sql in ["__NEED_CLARIFICATION__", "__NOT_DB__"]:
        app_logger.warning("SQL validation failed: Not a valid SQL query")
        return False, "Not a valid SQL query."

    # 1. Basic keyword check with word boundaries to avoid false positives (e.g., "created" containing "create")
    import re
    upper_sql = sql.upper()
    for keyword in BANNED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            app_logger.warning(f"SQL validation failed: Banned keyword found: {keyword}")
            return False, f"Banned keyword found: {keyword}"
            
    for func in RISKY_FUNCTIONS:
        if func in upper_sql:
            app_logger.warning(f"SQL validation failed: Risky function found: {func}")
            return False, f"Risky function found: {func}"

    # 2. Block multiple statements
    if ";" in sql:
        parts = [p.strip() for p in sql.split(";") if p.strip()]
        if len(parts) > 1:
            app_logger.warning("SQL validation failed: Multiple SQL statements found")
            return False, "Multiple SQL statements are not allowed."

    # 3. Block comments
    if "--" in sql or "/*" in sql:
        app_logger.warning("SQL validation failed: SQL comments found")
        return False, "SQL comments are not allowed."

    # 4. AST Validation
    try:
        parsed = sqlglot.parse_one(sql, read="mysql")
        
        # Must be a SELECT statement
        if not isinstance(parsed, exp.Select):
            app_logger.warning("SQL validation failed: Not a SELECT statement")
            return False, "Only SELECT queries are allowed."
            
        # Check tables used
        tables = [table.name.lower() for table in parsed.find_all(exp.Table)]
        for t in tables:
            if t not in [at.lower() for at in settings.ALLOWED_TABLES]:
                # Sometimes information_schema might be used by LLM? Not allowed by prompt rules.
                app_logger.warning(f"SQL validation failed: Table '{t}' is not in allowed list")
                return False, f"Table '{t}' is not in the allowed list."
                
        app_logger.info("SQL validation passed")
        return True, "SQL is safe."
    except Exception as e:
        app_logger.error(f"SQL validation failed with parsing error: {str(e)}")
        return False, f"SQL parsing error: {str(e)}"

if __name__ == "__main__":
    t1 = "SELECT * FROM data_so_summary"
    t2 = "DELETE FROM data_so_summary"
    t3 = "SELECT * FROM data_so_summary; DROP TABLE users"
    print(validate_sql(t1))
    print(validate_sql(t2))
    print(validate_sql(t3))

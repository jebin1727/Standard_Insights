import sqlglot
from sqlglot import exp
from app.core.config import ALLOWED_TABLES

BANNED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE"
]

RISKY_FUNCTIONS = [
    "SLEEP", "BENCHMARK", "LOAD_FILE", "INTO OUTFILE", "INTO DUMPFILE"
]

def validate_sql(sql: str):
    if not sql or sql in ["__NEED_CLARIFICATION__", "__NOT_DB__"]:
        return False, "Not a valid SQL query."

    # 1. Basic keyword check with word boundaries to avoid false positives (e.g., "created" containing "create")
    import re
    upper_sql = sql.upper()
    for keyword in BANNED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            return False, f"Banned keyword found: {keyword}"
            
    for func in RISKY_FUNCTIONS:
        if func in upper_sql:
            return False, f"Risky function found: {func}"

    # 2. Block multiple statements
    if ";" in sql:
        parts = [p.strip() for p in sql.split(";") if p.strip()]
        if len(parts) > 1:
            return False, "Multiple SQL statements are not allowed."

    # 3. Block comments
    if "--" in sql or "/*" in sql:
        return False, "SQL comments are not allowed."

    # 4. AST Validation
    try:
        parsed = sqlglot.parse_one(sql, read="mysql")
        
        # Must be a SELECT statement
        if not isinstance(parsed, exp.Select):
            return False, "Only SELECT queries are allowed."
            
        # Check tables used
        tables = [table.name.lower() for table in parsed.find_all(exp.Table)]
        for t in tables:
            if t not in [at.lower() for at in ALLOWED_TABLES]:
                # Sometimes information_schema might be used by LLM? Not allowed by prompt rules.
                return False, f"Table '{t}' is not in the allowed list."
                
        return True, "SQL is safe."
    except Exception as e:
        return False, f"SQL parsing error: {str(e)}"

if __name__ == "__main__":
    t1 = "SELECT * FROM data_so_summary"
    t2 = "DELETE FROM data_so_summary"
    t3 = "SELECT * FROM data_so_summary; DROP TABLE users"
    print(validate_sql(t1))
    print(validate_sql(t2))
    print(validate_sql(t3))

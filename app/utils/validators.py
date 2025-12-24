from typing import Any, Dict, List
import re


def validate_query_input(query: str) -> bool:
    """
    Validate user query input
    """
    if not query or not isinstance(query, str):
        return False
    
    # Check for excessive length
    if len(query.strip()) > 1000:
        return False
    
    # Check for potential injection patterns
    injection_patterns = [
        r"(?i)union\s+select",
        r"(?i)drop\s+table",
        r"(?i)exec\s*\(",
        r"(?i)sp_",
        r"(?i)xp_"
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, query):
            return False
    
    return True


def validate_sql_result(result: Any) -> Dict[str, Any]:
    """
    Validate and format SQL query results
    """
    if result is None:
        return {"status": "empty", "data": None, "message": "No results returned"}
    
    if isinstance(result, (int, float)):
        return {"status": "success", "data": result, "message": "Single value result"}
    
    if isinstance(result, list):
        if len(result) == 0:
            return {"status": "empty", "data": [], "message": "Empty result set"}
        return {"status": "success", "data": result, "message": f"List result with {len(result)} items"}
    
    return {"status": "success", "data": result, "message": "General result"}


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters/sequences
    sanitized = text.replace('\0', '').strip()
    return sanitized
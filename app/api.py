from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.schema_loader import fetch_schema
from app.core.retriever import SchemaRetriever
from app.core.time_ranges import get_time_context
from app.core.sql_generator import generate_sql
from app.core.sql_guard import validate_sql
from app.core.executor import execute_query
from app.core.responder import generate_natural_response

router = APIRouter()

# Initialize Schema RAG
schema_snippets = fetch_schema()
retriever = SchemaRetriever(schema_snippets)

class QueryRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask(request: QueryRequest):
    try:
        user_query = request.query
        
        # 1. Retrieve relevant schema (RAG)
        relevant_schema = retriever.retrieve(user_query, k=3)
        
        # 2. Get Time Context
        time_context = get_time_context()
        
        # 3. Generate SQL
        sql = generate_sql(user_query, relevant_schema, time_context)
        
        # 4. Handle non-SQL outputs
        if sql == "__NEED_CLARIFICATION__":
            return {
                "sql": None,
                "result": None,
                "natural_response": "I need more clarification to answer this question accurately."
            }
        if sql == "__NOT_DB__":
            return {
                "sql": None,
                "result": None,
                "natural_response": "This question does not seem to be related to the available business data."
            }
            
        # 5. SQL Safety Guard
        is_safe, message = validate_sql(sql)
        if not is_safe:
            return {
                "sql": None,
                "result": None,
                "natural_response": f"Safety Block: {message}. Query attempt: {sql}"
            }
            
        # 6. Execute SQL
        try:
            db_result = execute_query(sql)
        except Exception as e:
            return {
                "sql": sql,
                "result": None,
                "natural_response": f"Execution Error: {str(e)}"
            }
            
        # 7. Generate Response
        natural_response = generate_natural_response(user_query, sql, db_result)
        
        return {
            "sql": sql,
            "result": db_result,
            "natural_response": natural_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

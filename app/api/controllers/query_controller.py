from typing import Dict, Any, Optional
from app.services.rag_service import SchemaRetriever
from app.services.sql_generation_service import generate_sql
from app.services.safety_service import validate_sql
from app.services.response_service import generate_natural_response
from app.models.query.query_executor import execute_query
from app.models.schema.schema_manager import fetch_schema
from app.utils.time_utils import get_time_context
from app.utils.logger import app_logger
from app.utils.validators import validate_query_input


class QueryController:
    def __init__(self):
        app_logger.info("Initializing QueryController")
        # We'll fetch schema dynamically for each query to ensure it's current
        self.retriever = None
        app_logger.info("Query controller initialized. Schema will be fetched dynamically for each query.")

    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return the results
        """
        app_logger.info(f"Processing query: {user_query}")
        
        # Validate input
        if not validate_query_input(user_query):
            app_logger.warning(f"Invalid query input: {user_query}")
            return {
                "sql": None,
                "result": None,
                "natural_response": "Invalid query input. Please provide a valid natural language question."
            }
        
        try:
            # 1. Fetch current schema and create retriever
            try:
                schema_snippets = fetch_schema()
                retriever = SchemaRetriever(schema_snippets)
                app_logger.info(f"Schema fetched with {len(schema_snippets)} tables for query processing")
            except Exception as schema_error:
                app_logger.error(f"Error fetching schema: {str(schema_error)}")
                return {
                    "sql": None,
                    "result": None,
                    "natural_response": f"Database connection error: Unable to fetch schema information. Please check database connectivity. Error: {str(schema_error)}"
                }
            
            # 2. Retrieve relevant schema (RAG)
            relevant_schema = retriever.retrieve(user_query, k=3)
            app_logger.debug(f"Retrieved relevant schema: {relevant_schema[:100]}...")
            
            # 3. Get Time Context
            time_context = get_time_context()
            app_logger.debug("Time context retrieved")
            
            # 4. Generate SQL
            sql = generate_sql(user_query, relevant_schema, time_context)
            app_logger.info(f"Generated SQL: {sql[:100]}...")
            
            # 5. Handle non-SQL outputs
            if sql == "__NEED_CLARIFICATION__":
                app_logger.info("Query needs clarification")
                return {
                    "sql": None,
                    "result": None,
                    "natural_response": "I need more clarification to answer this question accurately."
                }
            if sql == "__NOT_DB__":
                app_logger.info("Query is not related to database")
                return {
                    "sql": None,
                    "result": None,
                    "natural_response": "This question does not seem to be related to the available business data."
                }
                
            # 6. SQL Safety Guard
            is_safe, message = validate_sql(sql)
            if not is_safe:
                app_logger.warning(f"SQL validation failed: {message}")
                return {
                    "sql": None,
                    "result": None,
                    "natural_response": f"Safety Block: {message}. Query attempt: {sql}"
                }
                
            # 7. Execute SQL
            try:
                db_result = execute_query(sql)
                app_logger.info("SQL query executed successfully")
            except Exception as e:
                app_logger.error(f"SQL execution error: {str(e)}")
                return {
                    "sql": sql,
                    "result": None,
                    "natural_response": f"Execution Error: {str(e)}"
                }
                
            # 8. Generate Response
            natural_response = generate_natural_response(user_query, sql, db_result)
            app_logger.info("Natural response generated successfully")
            
            return {
                "sql": sql,
                "result": db_result,
                "natural_response": natural_response
            }
            
        except Exception as e:
            app_logger.error(f"Error processing query: {str(e)}")
            raise
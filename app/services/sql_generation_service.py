from groq import Groq
from app.config.settings import settings
from app.utils.logger import app_logger

def get_groq_client():
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    return Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a MySQL expert. Generate ONLY the raw SQL query for the user's question.
Rules:
1. Use ONLY the provided schema.
2. Output ONLY raw SQL. No markdown, no explanations, no triple backticks.
3. Only SELECT queries are allowed.
4. If the question is ambiguous or cannot be answered using the schema, output exactly: __NEED_CLARIFICATION__
5. If the question is not related to the database, output exactly: __NOT_DB__
7. TABLE MAPPINGS:
   - Sales/Orders -> data_so_summary
   - Customers -> data_company_info
   - SKUs/Products -> data_prod_variant
   - Order Details -> data_so_details
8. JOINS:
   - Join data_so_summary and data_company_info on data_so_summary.client_id = data_company_info.dci_id.
"""

def generate_sql(query, schema_context, time_context):
    app_logger.info(f"Generating SQL for query: {query[:50]}...")
    full_prompt = (
        f"SCHEMA CONTEXT:\n{schema_context}\n\n"
        f"DATE CONTEXT:\n{time_context}\n\n"
        f"USER QUESTION: {query}"
    )
    
    try:
        client = get_groq_client()
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        
        sql = completion.choices[0].message.content.strip()
        # Cleanup in case LLM ignored "no backticks" rule
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        app_logger.info(f"SQL generated successfully: {sql[:100]}...")
        return sql
    except Exception as e:
        app_logger.error(f"Error generating SQL: {str(e)}")
        raise

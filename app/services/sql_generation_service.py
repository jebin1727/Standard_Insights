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
1. Use ONLY the column names that appear EXACTLY as provided in the schema below. Do not assume or invent column names.
2. Output ONLY raw SQL. No markdown, no explanations, no triple backticks.
3. Only SELECT queries are allowed.
4. If the question is ambiguous or cannot be answered using the schema, output exactly: __NEED_CLARIFICATION__
5. If the question is not related to the database, output exactly: __NOT_DB__
6. TABLE MAPPINGS:
   - Sales/Orders -> data_so_summary
   - Customers -> data_company_info
   - SKUs/Products -> data_prod_variant
   - Order Details -> data_so_details
7. ACTUAL COLUMN NAMES (CRITICAL - Use these exact names):
   - data_so_summary table has: dsosu_id (primary key), so_date, client_id (foreign key to data_company_info.dci_id), total_cost, price, etc.
   - data_company_info table has: dci_id (primary key), company_name, etc.
   - data_so_details table has: so_id (foreign key to data_so_summary.dsosu_id), etc.
   - data_prod_variant table has: dprodv_id (primary key), etc.
8. JOIN GUIDELINES:
   - Use proper joins: data_so_summary.client_id = data_company_info.dci_id
   - Use proper joins: data_so_details.so_id = data_so_summary.dsosu_id
   - DO NOT assume primary key column names like 'id', 'sos_id', 'so_id', 'sos_date', 'so_id', 'dss.so_id', etc.
   - Use ONLY the exact column names from the provided schema.
   - Look carefully at the column names in the schema to find proper join keys.
   - If you cannot determine the proper join conditions from the schema, return __NEED_CLARIFICATION__.
9. COLUMN GUIDELINES:
   - When looking for date columns, check the schema for columns like 'created', 'created_at', 'date', 'order_date', 'transaction_date', etc.
   - When looking for amount/price columns, check for 'total', 'total_amount', 'amount', 'price', 'cost', 'value', 'revenue', etc.
   - When looking for ID columns, check for 'client_id', 'customer_id', 'order_id', 'dci_id', etc. - but only use what exists in the schema.
   - If the schema doesn't contain the necessary columns to answer the question, return __NEED_CLARIFICATION__.
10. IMPORTANT: The schema information provided below contains ALL the available columns in the database. Use ONLY these column names and nothing else.
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

from groq import Groq
from app.config.settings import settings
from app.utils.logger import app_logger

def get_groq_client():
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    return Groq(api_key=settings.GROQ_API_KEY)

def generate_natural_response(query, sql, result):
    app_logger.info(f"Generating natural response for query: {query[:50]}...")
    if sql is None:
        app_logger.warning(f"No SQL provided, returning: {result}")
        return result # result contains the reason/refusal message
        
    prompt = (
        f"USER QUESTION: {query}\n"
        f"SQL EXECUTED: {sql}\n"
        f"DATABASE RESULT: {result}\n\n"
        "Generate a clear, human-readable business response based ONLY on the database result above.\n"
        "Instructions:\n"
        "1. Do not invent or hallucinate numbers.\n"
        "2. Use ₹ prefix for currency and format numbers with commas where appropriate.\n"
        "3. If the result is 'none' or empty, state that no records were found."
    )
    
    try:
        client = get_groq_client()
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful business data assistant. Summarize results accurately."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        response = completion.choices[0].message.content.strip()
        app_logger.info(f"Natural response generated successfully")
        return response
    except Exception as e:
        app_logger.error(f"Error generating natural response: {str(e)}")
        raise

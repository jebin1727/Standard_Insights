from groq import Groq
from app.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def generate_natural_response(query, sql, result):
    if sql is None:
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
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful business data assistant. Summarize results accurately."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3
    )
    
    return completion.choices[0].message.content.strip()

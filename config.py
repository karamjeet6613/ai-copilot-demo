import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
    SUPABASE_URL      = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    GEMINI_MODEL  = "gemini-2.0-flash"
    GROQ_MODEL    = "llama-3.3-70b-versatile"
    MAX_TOKENS    = 1500
    MAX_ITERATIONS = 5

    TEMPERATURE_CONFIG = {
        "agent":    0.1,
        "decision": 0.2,
        "factual":  0.2,
        "balanced": 0.4,
        "creative": 0.7,
    }

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def get_llm(mode: str = "balanced"):
    temp = Config.TEMPERATURE_CONFIG.get(mode, 0.4)
    return ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model=Config.GROQ_MODEL,
        temperature=temp,
        max_tokens=Config.MAX_TOKENS
    )
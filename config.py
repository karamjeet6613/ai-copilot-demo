import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
    SUPABASE_URL     = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    # LLM settings
    GEMINI_MODEL     = "gemini-2.0-flash"      # free tier model
    GROQ_MODEL       = "llama-3.3-70b-versatile"        # fast + free
    MAX_TOKENS       = 502
    TEMPERATURE      = 0.3

    # Agent settings
    MAX_ITERATIONS   = 6                        # agent reasoning steps
    VERBOSE          = True

    # In config.py — add after the Config class

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def get_llm(preference: str = "primary"):
    return ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model=Config.GROQ_MODEL,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )
    return ChatGoogleGenerativeAI(
        model=Config.GEMINI_MODEL,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=Config.TEMPERATURE,
        max_output_tokens=Config.MAX_TOKENS,
        convert_system_message_to_human=True
    )
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # LangSmith
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "eduagent")

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_STORE_PATH: str = os.path.join(BASE_DIR, "docs_store")
    CHROMA_PATH: str = os.path.join(BASE_DIR, "chroma_db")
    DB_PATH: str = os.path.join(BASE_DIR, "eduagent.db")

settings = Settings()

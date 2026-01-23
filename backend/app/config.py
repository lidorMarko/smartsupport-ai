from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"

    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 3

    # ChromaDB
    chroma_persist_directory: str = "./data/chroma_db"
    collection_name: str = "documents"

    # Email Settings (Gmail SMTP)
    smtp_email: str = ""  # Your Gmail address
    smtp_password: str = ""  # Gmail App Password

    # App settings
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()

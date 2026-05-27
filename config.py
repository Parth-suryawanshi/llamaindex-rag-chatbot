import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "llamaindex_rag_documents"

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    DATA_DIR: str = "data"
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 4

    RESET_COLLECTION: bool = False
    CHAT_HISTORY_FILE: str = "chat_history.json"


def get_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.lower() in ["true", "1", "yes", "y"]


def get_config() -> AppConfig:
    groq_api_key = os.getenv("GROQ_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not available in .env file")

    if not qdrant_url:
        raise ValueError("QDRANT_URL is not available in .env file")

    return AppConfig(
        GROQ_API_KEY=groq_api_key,
        GROQ_MODEL=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),

        QDRANT_URL=qdrant_url,
        QDRANT_API_KEY=os.getenv("QDRANT_API_KEY") or None,
        QDRANT_COLLECTION=os.getenv("QDRANT_COLLECTION", "llamaindex_rag_documents"),

        EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),

        DATA_DIR=os.getenv("DATA_DIR", "data"),
        CHUNK_SIZE=int(os.getenv("CHUNK_SIZE", "1024")),
        CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP", "150")),
        TOP_K=int(os.getenv("TOP_K", "4")),

        RESET_COLLECTION=get_bool(os.getenv("RESET_COLLECTION"), False),
        CHAT_HISTORY_FILE=os.getenv("CHAT_HISTORY_FILE", "chat_history.json"),
    )
  
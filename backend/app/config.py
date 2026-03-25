"""
CRI-RSK Chatbot — Application Configuration.
Centralized settings using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")

    # Supabase
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")

    # Paths
    knowledge_base_path: str = Field(
        default="./knowledge_base", alias="KNOWLEDGE_BASE_PATH"
    )
    chroma_persist_dir: str = Field(
        default="./chroma_data", alias="CHROMA_PERSIST_DIR"
    )

    # Model settings
    embedding_model: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        alias="EMBEDDING_MODEL",
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        alias="RERANKER_MODEL",
    )
    llm_model: str = Field(
        default="gemini-2.5-flash", alias="LLM_MODEL"
    )

    anonymized_telemetry: bool = Field(default=False, alias="ANONYMIZED_TELEMETRY")

    # Upstash Redis (for OTP)
    upstash_redis_url: str = Field(default="", alias="UPSTASH_REDIS_REST_URL")
    upstash_redis_token: str = Field(default="", alias="UPSTASH_REDIS_REST_TOKEN")

    # RAG settings
    retrieval_top_k: int = 10
    rerank_top_k: int = 3
    fusion_alpha: float = 0.5  # weight for vector vs BM25
    enable_reranking: bool = Field(default=True, alias="ENABLE_RERANKING")

    # App
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


def get_settings() -> Settings:
    """Create and return settings instance."""
    return Settings()

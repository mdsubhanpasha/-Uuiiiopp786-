"""
PASHA-NEURO-RAG Configuration Settings
Author: Mohammad Subhan Pasha
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "PASHA-NEURO-RAG"
    AUTHOR: str = "Mohammad Subhan Pasha"
    VERSION: str = "1.0.0"

    # OpenAI Settings
    OPENAI_API_KEY: str = Field(default="sk-placeholder-key")
    LLM_MODEL: str = Field(default="gpt-4o")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-large")

    # Qdrant Vector DB
    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION_NAME: str = Field(default="pasha_neuro_rag")
    VECTOR_SIZE: int = Field(default=3072)  # text-embedding-3-large dimension

    # Hybrid Search & Reranking
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5
    RERANKER_MODEL: str = Field(default="BAAI/bge-reranker-large")
    COHERE_API_KEY: str = Field(default="")

    # DeBERTa-v3 NLI Validator (Hallucination Guard)
    NLI_MODEL_NAME: str = Field(default="cross-encoder/nli-deberta-v3-base")
    GROUNDEDNESS_THRESHOLD: float = Field(default=0.70)

    # Self-RAG Loop Parameters
    CONFIDENCE_THRESHOLD: float = Field(default=0.85)
    MAX_SELF_CORRECTION_ITERATIONS: int = Field(default=3)

    # Observability
    LANGCHAIN_TRACING_V2: str = Field(default="false")
    LANGCHAIN_API_KEY: str = Field(default="")
    LANGCHAIN_PROJECT: str = Field(default="pasha-neuro-rag")


settings = Settings()

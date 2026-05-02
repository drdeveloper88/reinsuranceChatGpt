from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum

class LLMType(str, Enum):
    """Supported LLM types"""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"

class EmbeddingType(str, Enum):
    """Supported embedding types"""
    OPENAI = "openai"
    SENTENCE_TRANSFORMER = "sentence-transformer"
    OLLAMA = "ollama"

class VectorDBType(str, Enum):
    """Supported vector database types"""
    CHROMA = "chroma"
    MILVUS = "milvus"

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Insurance ChatBot API"
    environment: str = "development"
    debug: bool = True
    
    # LLM Configuration
    llm_type: LLMType = LLMType.OLLAMA
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"  # Free, lightweight model
    huggingface_model_name: Optional[str] = "mistralai/Mistral-7B-v0.1"
    huggingface_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # LLM Parameters
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024
    llm_top_p: float = 0.95
    
    # Embedding Configuration
    embedding_type: EmbeddingType = EmbeddingType.SENTENCE_TRANSFORMER
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Vector Database Configuration
    vector_db_type: VectorDBType = VectorDBType.CHROMA
    chroma_persist_dir: str = "./.chroma_data"
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "insurance_chatbot"
    
    # RAG Configuration
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.5
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Authentication & Security
    jwt_secret: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:4200", "http://localhost:3000", "http://localhost:8100"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Insurance Domain Configuration
    domain_context: str = "insurance"  # insurance, health, property, auto, life
    max_document_size_mb: int = 25
    max_documents_per_upload: int = 100
    enable_document_validation: bool = True
    
    # Redis Configuration (for caching - optional)
    redis_url: Optional[str] = "redis://localhost:6379"
    cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

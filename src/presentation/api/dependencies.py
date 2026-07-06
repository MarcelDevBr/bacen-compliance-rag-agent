from functools import lru_cache

from src.domain.entities import AppConfig
from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.reranker_port import RerankerPort

from src.infrastructure.config.config_loader import load_config
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.infrastructure.reranker.reranker_adapter import CrossEncoderRerankerAdapter

@lru_cache()
def get_config() -> AppConfig:
    """Carrega as configurações apenas uma vez e as armazena em cache."""
    return load_config()

@lru_cache()
def get_vector_store() -> VectorStorePort:
    """Inicializa o banco vetorial apenas uma vez usando o cache nativo (Singleton)."""
    return VectorStoreAdapter(config=get_config())

@lru_cache()
def get_llm() -> LLMPort:
    """Inicializa o adaptador LLM apenas uma vez."""
    return LLMAdapter(config=get_config())

@lru_cache()
def get_reranker() -> RerankerPort:
    """Inicializa o modelo pesado de reranking apenas uma vez."""
    return CrossEncoderRerankerAdapter()

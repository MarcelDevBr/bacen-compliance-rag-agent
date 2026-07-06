from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.reranker_port import RerankerPort

from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.infrastructure.reranker.reranker_adapter import CrossEncoderRerankerAdapter

# Singletons em nível de módulo para garantir que as redes neurais
# pesadas sejam carregadas apenas uma vez na memória durante a inicialização.
_vector_store_instance = None
_llm_instance = None
_reranker_instance = None

def get_vector_store() -> VectorStorePort:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreAdapter()
    return _vector_store_instance

def get_llm() -> LLMPort:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMAdapter()
    return _llm_instance

def get_reranker() -> RerankerPort:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = CrossEncoderRerankerAdapter()
    return _reranker_instance

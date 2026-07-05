"""
Módulo de testes automatizados para a camada de infraestrutura.

Valida a inicialização correta dos adaptadores LLM (Groq) e banco vetorial (ChromaDB),
garantindo resiliência e fail-fast em ausência de variáveis de ambiente.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter

@patch("src.infrastructure.llm.llm_adapter.os.getenv")
@patch("src.infrastructure.llm.llm_adapter.LLM")
def test_llm_adapter(mock_llm_class, mock_getenv) -> None:
    """
    Testa a inicialização do adaptador de LLM.
    O método os.getenv é simulado (mock) para injetar uma chave de API fictícia, e a classe LLM
    do CrewAI é interceptada para evitar instanciamento real de rede.
    """
    mock_getenv.return_value = "fake-key"
    mock_llm_class.return_value = MagicMock()
    adapter = LLMAdapter()
    assert adapter.config is not None
    assert adapter.get_client() is not None

@patch("src.infrastructure.llm.llm_adapter.os.getenv")
def test_llm_adapter_missing_key(mock_getenv) -> None:
    """
    Garante o acionamento (raise) de exceção na ausência de API_KEY no ambiente.
    """
    mock_getenv.return_value = None
    with pytest.raises(ValueError):
        LLMAdapter()

@patch("src.infrastructure.vector_store.vector_store_adapter.chromadb.PersistentClient")
def test_vector_store_adapter_init(mock_chroma_client) -> None:
    """
    Testa a inicialização do banco ChromaDB.
    Verifica se a coleção persistida é criada/carregada adequadamente.
    """
    mock_db = MagicMock()
    mock_chroma_client.return_value = mock_db
    
    adapter = VectorStoreAdapter(persist_dir="test_dir")
    vs = adapter.get_vector_store()
    
    assert vs is not None
    mock_db.get_or_create_collection.assert_called_once_with("bacen_collection")

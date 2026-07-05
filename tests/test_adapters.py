"""
Módulo de testes automatizados para a camada de infraestrutura.

Valida a inicialização correta dos adaptadores LLM (Groq) e banco vetorial (ChromaDB),
garantindo resiliência e fail-fast em ausência de variáveis de ambiente.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.vector_store.chromadb_adapter import ChromaDBAdapter
from src.infrastructure.llm.groq_adapter import GroqAdapter

@patch("src.infrastructure.llm.groq_adapter.os.getenv")
@patch("src.infrastructure.llm.groq_adapter.ChatGroq")
def test_groq_adapter(mock_chat_groq, mock_getenv) -> None:
    """
    Testa a inicialização do adaptador Groq.
    O método os.getenv é simulado (mock) para injetar uma chave de API fictícia, e a classe ChatGroq
    é interceptada para evitar chamadas reais de rede. Este teste valida a correta instanciação 
    do cliente LLM pelo adaptador.
    """
    mock_getenv.return_value = "fake-key"
    mock_chat_groq.return_value = MagicMock()
    adapter = GroqAdapter()
    assert adapter.config is not None
    assert adapter.get_client() is not None

@patch("src.infrastructure.llm.groq_adapter.os.getenv")
def test_groq_adapter_missing_key(mock_getenv) -> None:
    """
    Garante o acionamento (raise) de exceção na ausência de API_KEY no ambiente.
    """
    mock_getenv.return_value = None
    with pytest.raises(ValueError):
        GroqAdapter()

@patch("src.infrastructure.vector_store.chromadb_adapter.chromadb.PersistentClient")
def test_chromadb_adapter_init(mock_chroma_client) -> None:
    """
    Testa a inicialização do banco ChromaDB.
    Verifica se a coleção persistida é criada/carregada adequadamente.
    """
    mock_db = MagicMock()
    mock_chroma_client.return_value = mock_db
    
    adapter = ChromaDBAdapter(persist_dir="test_dir")
    vs = adapter.get_vector_store()
    
    assert vs is not None
    mock_db.get_or_create_collection.assert_called_once_with("bacen_collection")

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

@patch("src.infrastructure.vector_store.vector_store_adapter.VectorStoreAdapter.get_vector_store")
@patch("llama_index.core.VectorStoreIndex")
@patch("llama_index.embeddings.huggingface.HuggingFaceEmbedding")
def test_vector_store_adapter_search_and_retriever(mock_hf, mock_vsi, mock_get_store) -> None:
    mock_index = MagicMock()
    mock_retriever = MagicMock()
    mock_node = MagicMock()
    # Pydantic validates types, so we need real strings/numbers for mocked fields
    mock_node.node.text = "mocked text"
    mock_node.node.metadata = {"file_name": "test.pdf", "page_label": "2"}
    mock_node.score = 0.95
    
    mock_retriever.retrieve.return_value = [mock_node]
    mock_index.as_retriever.return_value = mock_retriever
    mock_vsi.from_vector_store.return_value = mock_index

    adapter = VectorStoreAdapter()
    
    texts, citations = adapter.search("teste", top_k=1)
    
    assert len(texts) == 1
    assert texts[0] == "mocked text"
    assert len(citations) == 1
    assert citations[0].source_file == "test.pdf"
    assert citations[0].page_number == 2
    
    assert mock_retriever.retrieve.called
    assert mock_vsi.from_vector_store.called

    retriever = adapter.as_retriever()
    assert retriever == mock_retriever

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

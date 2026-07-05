import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.vector_store.faiss_adapter import FaissDBAdapter
from src.infrastructure.llm.groq_adapter import GroqAdapter

@patch("src.infrastructure.llm.groq_adapter.os.getenv")
@patch("src.infrastructure.llm.groq_adapter.ChatGroq")
def test_groq_adapter(mock_chat_groq, mock_getenv):
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
def test_groq_adapter_missing_key(mock_getenv):
    mock_getenv.return_value = None
    with pytest.raises(ValueError):
        GroqAdapter()

@patch("src.infrastructure.vector_store.faiss_adapter.os.path.exists")
@patch("src.infrastructure.vector_store.faiss_adapter.faiss")
def test_faiss_adapter_create_new(mock_faiss, mock_exists):
    """
    Testa a inicialização do banco FAISS na ausência de índice persistido no disco.
    A função os.path.exists é simulada para retornar False, assegurando a criação de
    um novo índice IndexFlatL2 em memória.
    """
    mock_exists.return_value = False
    mock_faiss.IndexFlatL2.return_value = MagicMock()
    
    adapter = FaissDBAdapter(persist_dir="test_dir")
    vs = adapter.get_vector_store()
    assert vs is not None

@patch("src.infrastructure.vector_store.faiss_adapter.os.path.exists")
@patch("src.infrastructure.vector_store.faiss_adapter.faiss")
def test_faiss_adapter_load_existing(mock_faiss, mock_exists):
    mock_exists.return_value = True
    mock_faiss.read_index.return_value = MagicMock()
    
    adapter = FaissDBAdapter(persist_dir="test_dir")
    vs = adapter.get_vector_store()
    assert vs is not None

def test_faiss_adapter_save():
    adapter = FaissDBAdapter(persist_dir="test_dir")
    mock_vs = MagicMock()
    adapter.save(mock_vs)
    mock_vs.client.write_index.assert_called_once_with(adapter.persist_path)

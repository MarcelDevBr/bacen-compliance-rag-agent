"""
Módulo de testes automatizados para a camada de infraestrutura.

Valida a inicialização correta dos adaptadores LLM (Groq) e banco vetorial (ChromaDB),
garantindo resiliência e fail-fast em ausência de variáveis de ambiente.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.infrastructure.reranker.reranker_adapter import CrossEncoderRerankerAdapter
from src.domain.entities import AppConfig, Citation

# Helper fixture-like to create a dummy config
def get_mock_config() -> AppConfig:
    from src.domain.entities import AppMetadata, Environment, LLMConfig, RAGConfig, RetrieverConfig, RerankerConfig, VectorStoreConfig, TelemetryConfig, TelemetryLangfuse, PromptsConfig, AgentPromptConfig
    return AppConfig(
        app=AppMetadata(name="Test", environment=Environment.DEVELOPMENT, host="0.0.0.0", port_api=80, port_ui=80),
        llm=LLMConfig(),
        rag=RAGConfig(retriever=RetrieverConfig(), reranker=RerankerConfig(), vector_store=VectorStoreConfig(persist_dir="mock_dir", collection_name="bacen_collection", embed_model="mock")),
        telemetry=TelemetryConfig(langfuse=TelemetryLangfuse()),
        prompts=PromptsConfig(analyst=AgentPromptConfig(system="s", user="u"), reviewer=AgentPromptConfig(system="s", user="u"))
    )

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
    adapter = LLMAdapter(config=get_mock_config())
    assert adapter.config is not None
    assert adapter.get_client() is not None

@patch("src.infrastructure.vector_store.vector_store_adapter.VectorStoreAdapter.get_vector_store")
@patch("src.infrastructure.vector_store.vector_store_adapter.VectorStoreIndex")
@patch("src.infrastructure.vector_store.vector_store_adapter.HuggingFaceEmbedding")
def test_vector_store_adapter_search_and_retriever(mock_hf, mock_vsi, mock_get_store) -> None:
    mock_index = MagicMock()
    mock_retriever = MagicMock()
    mock_node = MagicMock()
    # Pydantic validates types, so we need real strings/numbers for mocked fields
    mock_node.node.get_content.return_value = "mocked text"
    # Provide an invalid page_label to trigger ValueError coverage
    mock_node.node.metadata = {"file_name": "test.pdf", "page_label": "invalid_page"}
    mock_node.score = 0.95
    
    mock_retriever.retrieve.return_value = [mock_node]
    mock_index.as_retriever.return_value = mock_retriever
    mock_vsi.from_vector_store.return_value = mock_index

    adapter = VectorStoreAdapter(config=get_mock_config())
    
    texts, citations = adapter.search("teste", top_k=1)
    
    assert len(texts) == 1
    assert texts[0] == "mocked text"
    assert len(citations) == 1
    assert citations[0].source_file == "test.pdf"
    assert citations[0].page_number == 1
    
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
    adapter = LLMAdapter(config=get_mock_config())
    with pytest.raises(ValueError):
        adapter.get_client("google")

@patch("src.infrastructure.llm.llm_adapter.os.getenv")
@patch("src.infrastructure.llm.llm_adapter.LLM")
def test_llm_adapter_groq(mock_llm_class, mock_getenv) -> None:
    mock_getenv.side_effect = lambda k: "fake-groq" if k == "GROQ_API_KEY" else "fake-gemini"
    adapter = LLMAdapter(config=get_mock_config())
    client = adapter.get_client(provider_override="groq")
    assert client is not None

@patch("src.infrastructure.llm.llm_adapter.os.getenv")
def test_llm_adapter_groq_missing_key(mock_getenv) -> None:
    mock_getenv.return_value = None
    adapter = LLMAdapter(config=get_mock_config())
    with pytest.raises(ValueError):
        adapter.get_client("groq")

@patch("src.infrastructure.vector_store.vector_store_adapter.VectorStoreIndex")
@patch("src.infrastructure.vector_store.vector_store_adapter.HuggingFaceEmbedding")
@patch("src.infrastructure.vector_store.vector_store_adapter.chromadb.PersistentClient")
def test_vector_store_adapter_init(mock_chroma_client, mock_hf, mock_vsi) -> None:
    """
    Testa a inicialização do banco ChromaDB.
    Verifica se a coleção persistida é criada/carregada adequadamente.
    """
    mock_db = MagicMock()
    mock_chroma_client.return_value = mock_db
    
    adapter = VectorStoreAdapter(config=get_mock_config())
    vs = adapter.get_vector_store()
    
    assert vs is not None
    assert adapter.as_retriever() is not None
    mock_db.get_or_create_collection.assert_called_once_with("bacen_collection")

@patch("src.infrastructure.reranker.reranker_adapter.CrossEncoder")
@patch("src.infrastructure.reranker.reranker_adapter.load_config")
def test_reranker_adapter(mock_load_config, mock_cross_encoder):
    mock_load_config.return_value = get_mock_config()
    mock_model = MagicMock()
    # Predict returns a list of scores
    mock_model.predict.return_value = [0.9, 0.2]
    mock_cross_encoder.return_value = mock_model

    adapter = CrossEncoderRerankerAdapter()
    
    docs = ["Doc 1", "Doc 2"]
    cits = [Citation(source_file="A", page_number=1, text_snippet="", relevance_score=0.0), 
            Citation(source_file="B", page_number=2, text_snippet="", relevance_score=0.0)]
            
    # Test normal rerank
    top_docs, top_cits = adapter.rerank("Query", docs, cits)
    assert len(top_docs) == 2
    assert top_docs[0] == "Doc 1"
    assert top_cits[0].relevance_score == 0.9

    # Test empty docs
    empty_docs, empty_cits = adapter.rerank("Query", [], [])
    assert empty_docs == []
    assert empty_cits == []

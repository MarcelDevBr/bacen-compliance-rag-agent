"""
Módulo de testes unitários da Orquestração do LangGraph.
"""

from unittest.mock import patch, MagicMock
from src.application.use_cases.rag_orchestrator import retrieve_node, rerank_node, generate_node, build_graph

@patch("src.application.use_cases.rag_orchestrator.VectorStorePort")
def test_retrieve_node(mock_vector_port_class) -> None:
    """
    Testa unitariamente o nó de recuperação (retriever) no LangGraph.
    Verifica se a chamada à busca vetorial ocorre corretamente com a abstração do VectorStorePort.
    """
    mock_vector_port = MagicMock()
    
    from src.domain.entities import Citation
    fake_citations = [
        Citation(source_file="doc1.pdf", page_number=1, text_snippet="...", relevance_score=0.9),
        Citation(source_file="doc2.pdf", page_number=2, text_snippet="...", relevance_score=0.8)
    ]
    mock_vector_port.search.return_value = (["Regulamento Pix: Art 1. ...", "Art 2. O MED..."], fake_citations)
    
    state_input = {"question": "O que é MED?"}
    
    result = retrieve_node(state_input, vector_store_port=mock_vector_port)
    assert len(result["documents"]) == 2
    assert len(result["citations"]) == 2
    mock_vector_port.search.assert_called_once_with("O que é MED?")

def test_rerank_node() -> None:
    """
    Testa unitariamente o nó de re-ranking injetando o RerankerPort.
    """
    mock_reranker_port = MagicMock()
    
    from src.domain.entities import Citation
    fake_citations = [
        Citation(source_file="doc1.pdf", page_number=1, text_snippet="...", relevance_score=0.9),
        Citation(source_file="doc2.pdf", page_number=2, text_snippet="...", relevance_score=0.8)
    ]
    
    # Simula o reranker retornando apenas o primeiro documento após ordenação
    mock_reranker_port.rerank.return_value = (["Regulamento Pix: Art 1. ..."], [fake_citations[0]])
    
    state_input = {
        "question": "O que é MED?",
        "documents": ["Regulamento Pix: Art 1. ...", "Art 2. O MED..."],
        "citations": fake_citations
    }
    
    result = rerank_node(state_input, reranker_port=mock_reranker_port)
    assert len(result["documents"]) == 1
    assert len(result["citations"]) == 1
    mock_reranker_port.rerank.assert_called_once()
    
def test_rerank_node_empty() -> None:
    """
    Verifica comportamento do reranker quando não há documentos.
    """
    mock_reranker_port = MagicMock()
    state_input = {"question": "O que é MED?", "documents": [], "citations": []}
    result = rerank_node(state_input, reranker_port=mock_reranker_port)
    assert result == {}
    mock_reranker_port.rerank.assert_not_called()

@patch("src.application.use_cases.rag_orchestrator.ComplianceSquad")
@patch("src.application.use_cases.rag_orchestrator.LLMPort")
def test_generate_node(mock_llm_port_class, mock_squad_class) -> None:
    """
    Testa unitariamente o nó de geração (generator).
    Valida se a delegação ao Squad Multi-Agente ocorre perfeitamente.
    """
    mock_squad_instance = MagicMock()
    mock_squad_instance.run_squad.return_value = "Squad final answer"
    mock_squad_class.return_value = mock_squad_instance
    mock_llm_port = MagicMock()

    state_input = {
        "question": "Prazo do MED?",
        "documents": ["O prazo é de 7 dias."]
    }
    
    from tests.test_adapters import get_mock_config
    result = generate_node(state_input, llm_port=mock_llm_port, app_config=get_mock_config())
    
    assert result["final_answer"] == "Squad final answer"

@patch("src.application.use_cases.rag_orchestrator.StateGraph")
def test_build_graph(mock_stategraph) -> None:
    """
    Verifica se a construção e compilação do grafo ocorrem com sucesso utilizando Injeção de Dependência completa.
    """
    mock_builder = MagicMock()
    mock_stategraph.return_value = mock_builder
    
    mock_vector = MagicMock()
    mock_llm = MagicMock()
    mock_reranker = MagicMock()
    
    from tests.test_adapters import get_mock_config
    build_graph(vector_store_port=mock_vector, llm_port=mock_llm, reranker_port=mock_reranker, app_config=get_mock_config())
    
    assert mock_stategraph.called

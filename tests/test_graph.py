"""
Módulo de testes unitários da Orquestração do LangGraph.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.application.use_cases.rag_orchestrator import retrieve_node, generate_node, build_graph
from src.domain.entities import ComplianceResponse

@patch("src.application.use_cases.rag_orchestrator.VectorStorePort")
def test_retrieve_node(mock_vector_port_class) -> None:
    """
    Testa unitariamente o nó de recuperação (retriever) no LangGraph.
    Verifica se a chamada à busca vetorial ocorre corretamente com a abstração do VectorStorePort.
    """
    mock_vector_port = MagicMock()
    mock_vector_port.search.return_value = ["Regulamento Pix: Art 1. ...", "Art 2. O MED..."]
    
    state_input = {"question": "O que é MED?"}
    
    result = retrieve_node(state_input, vector_store_port=mock_vector_port)
    assert len(result["documents"]) == 2
    mock_vector_port.search.assert_called_once_with("O que é MED?", top_k=3)

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
    
    result = generate_node(state_input, llm_port=mock_llm_port)
    assert result["final_answer"] == "Squad final answer"

@patch("src.application.use_cases.rag_orchestrator.StateGraph")
def test_build_graph(mock_stategraph) -> None:
    """
    Verifica se a construção e compilação do grafo ocorrem com sucesso.
    """
    mock_builder = MagicMock()
    mock_stategraph.return_value = mock_builder
    
    mock_vector = MagicMock()
    mock_llm = MagicMock()
    
    app = build_graph(vector_store_port=mock_vector, llm_port=mock_llm)
    assert mock_builder.compile.called

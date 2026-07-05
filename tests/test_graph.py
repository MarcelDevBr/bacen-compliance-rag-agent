"""
Módulo de testes automatizados para a camada de orquestração via LangGraph.

Este módulo assegura que os nós isolados (nodes) da máquina de estados (StateGraph)
produzem transformações determinísticas no estado global injetado durante as execuções.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.application.graph import retrieve_node, generate_node, build_graph

@patch("src.application.graph.VectorStoreIndex")
@patch("src.application.graph.HuggingFaceEmbedding")
@patch("src.application.graph.VectorStoreAdapter")
def test_retrieve_node(mock_vector_store_adapter, mock_embed, mock_index) -> None:
    """
    Valida a unidade funcional de recuperação vetorial (Retrieval Node).
    Módulos fundamentais (ChromaDB, Embeddings) são simulados (mocked), 
    certificando que os documentos recuperados são devidamente indexados no GraphState.
    """
    mock_retriever = MagicMock()
    mock_node = MagicMock()
    mock_node.text = "Mocked text context"
    mock_retriever.retrieve.return_value = [mock_node]
    
    mock_index.from_vector_store.return_value.as_retriever.return_value = mock_retriever
    
    state = {"question": "Test question"}
    new_state = retrieve_node(state)
    assert "Mocked text context" in new_state["documents"]

@patch("src.application.graph.ComplianceAgents")
def test_generate_node(mock_agents) -> None:
    """
    Valida a unidade funcional de inferência do pipeline (Generation Node).
    Isola o esquadrão multi-agente, avaliando a captura do output da rede de LLMs 
    e a correta inserção da chave 'final_answer' no dict de estado subjacente.
    """
    mock_agents.return_value.run_squad.return_value = "Squad final answer"
    state = {"question": "Q", "documents": ["Doc1"]}
    res = generate_node(state)
    assert res["final_answer"] == "Squad final answer"

@patch("src.application.graph.StateGraph")
def test_build_graph(mock_stategraph) -> None:
    """
    Valida a construção computacional do fluxo cíclico.
    Asegura que o método 'compile' foi acionado para travamento e compilação estrutural do Grafo.
    """
    mock_builder = MagicMock()
    mock_stategraph.return_value = mock_builder
    
    graph = build_graph()
    assert mock_builder.compile.called

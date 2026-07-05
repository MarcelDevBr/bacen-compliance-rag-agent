import pytest
from unittest.mock import patch, MagicMock
from src.application.graph import retrieve_node, generate_node, build_graph

@patch("src.application.graph.VectorStoreIndex")
@patch("src.application.graph.HuggingFaceEmbedding")
@patch("src.application.graph.FaissDBAdapter")
def test_retrieve_node(mock_faiss_db, mock_embed, mock_index):
    mock_retriever = MagicMock()
    mock_node = MagicMock()
    mock_node.text = "Mocked text context"
    mock_retriever.retrieve.return_value = [mock_node]
    
    mock_index.from_vector_store.return_value.as_retriever.return_value = mock_retriever
    
    state = {"question": "Test question"}
    new_state = retrieve_node(state)
    assert "Mocked text context" in new_state["documents"]

@patch("src.application.graph.ComplianceAgents")
def test_generate_node(mock_agents):
    mock_agents.return_value.run_squad.return_value = "Squad final answer"
    state = {"question": "Q", "documents": ["Doc1"]}
    res = generate_node(state)
    assert res["final_answer"] == "Squad final answer"

@patch("src.application.graph.StateGraph")
def test_build_graph(mock_stategraph):
    mock_builder = MagicMock()
    mock_stategraph.return_value = mock_builder
    
    graph = build_graph()
    assert mock_builder.compile.called

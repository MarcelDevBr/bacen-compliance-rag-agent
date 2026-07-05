import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.presentation.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_ui_serves_html():
    response = client.get("/")
    assert response.status_code == 200

def test_invalid_query_request():
    response = client.post("/api/v1/query", json={"thread_id": "123"})
    assert response.status_code == 422

@patch("src.presentation.api.main.os.path.join")
def test_ui_not_found(mock_join):
    mock_join.return_value = "fake_path_does_not_exist.html"
    response = client.get("/")
    assert response.status_code == 200
    assert "não encontrada" in response.text

@patch("src.presentation.api.routes.rag_graph.invoke")
def test_ask_compliance_success(mock_invoke):
    mock_invoke.return_value = {"final_answer": "Mock Answer"}
    response = client.post("/api/v1/query", json={"query": "Test", "thread_id": "123"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Mock Answer"

@patch("src.presentation.api.routes.rag_graph.invoke")
def test_ask_compliance_error(mock_invoke):
    mock_invoke.side_effect = Exception("Graph fail")
    response = client.post("/api/v1/query", json={"query": "Test", "thread_id": "123"})
    assert response.status_code == 500
    assert "Erro interno" in response.json()["detail"]

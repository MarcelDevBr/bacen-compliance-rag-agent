"""
Módulo de testes automatizados para a camada de infraestrutura de roteamento e apresentação.

Este módulo concentra as rotinas de verificação do FastAPI, testando 
respostas de sondas de saúde (health checks), renderização de UI e comportamento 
de endpoints sob condições normais e de exceção.
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pytest
import json
from fastapi import Request

from src.presentation.api.main import app, global_exception_handler
from src.domain.messages import Messages

client = TestClient(app)

def test_health_check() -> None:
    """
    Testa o endpoint de health check da aplicação.
    Valida se o serviço está operante retornando status HTTP 200.
    """
    response = client.get("/health")
    assert response.status_code == 200



def test_invalid_query_request() -> None:
    """
    Valida o comportamento da API diante de requisições malformadas.
    Espera-se a rejeição estruturada (Unprocessable Entity - 422) via Pydantic.
    """
    response = client.post("/api/v1/query", json={"thread_id": "123"})
    assert response.status_code == 422



@patch("src.presentation.api.routes.build_graph")
def test_ask_compliance_success(mock_build_graph) -> None:
    """
    Testa a funcionalidade nominal (Happy Path) da requisição ao RAG.
    O grafo de execução é interceptado (mock) garantindo teste isolado sem acesso a redes.
    """
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"final_answer": "Mock Answer"}
    mock_build_graph.return_value = mock_graph
    
    response = client.post("/api/v1/query", json={"query": "Test", "thread_id": "123"})
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["answer"] == "Mock Answer"

@patch("src.presentation.api.routes.build_graph")
def test_ask_compliance_error(mock_build_graph) -> None:
    """
    Avalia a mitigação de erros internos durante o processamento de inferência.
    Força-se uma exceção no componente orquestrador, aferindo se a falha é convertida
    adequadamente em um código HTTP 500 (Internal Server Error).
    """
    mock_graph = MagicMock()
    mock_graph.invoke.side_effect = Exception("Graph fail")
    mock_build_graph.return_value = mock_graph
    
    response = client.post("/api/v1/query", json={"query": "Test", "thread_id": "123"})
    
    assert response.status_code == 500
    assert response.json()["success"] is False
    assert Messages.RAG_EXECUTION_FAILED in response.json()["error_message"]
    assert response.json()["error_code"] == "ORCHESTRATION_ERROR"

@pytest.mark.asyncio
async def test_global_exception_handler_direct() -> None:
    req = MagicMock(spec=Request)
    req.url = "http://test"
    response = await global_exception_handler(req, Exception("Test"))
    assert response.status_code == 500
    data = json.loads(response.body)
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"

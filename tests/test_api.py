import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app

client = TestClient(app)

def test_health_check():
    """Testa se o endpoint de verificação de integridade está funcional."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Sistema de Compliance Operacional" in data["message"]

def test_ui_serves_html():
    """Testa se a raiz (/) está devolvendo conteúdo HTML da Interface Gráfica."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text.lower()
    
def test_invalid_query_request():
    """Testa a validação do Pydantic barrando payloads inválidos."""
    # Envia um body sem o campo obrigatório 'query'
    response = client.post("/api/v1/query", json={"thread_id": "123"})
    assert response.status_code == 422 # Unprocessable Entity (Falha Pydantic)

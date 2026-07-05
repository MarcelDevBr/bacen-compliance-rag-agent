"""
Módulo de testes automatizados para a camada de Domínio.

Valida a resiliência e as restrições estritas dos objetos de valor,
estruturas de dados e funções de inicialização da camada fundamental da Arquitetura Hexagonal.
"""

import pytest
from src.infrastructure.config.config_loader import load_config

def test_config_loader_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Testa a mecânica de restrição (Fail-Fast) do carregador de configuração.
    Espera-se o lançamento da exceção FileNotFoundError na ausência do arquivo base (config.yml).
    """
    with pytest.raises(FileNotFoundError):
        load_config(config_path="inexistente_123.yml")

def test_exceptions() -> None:
    """Valida instanciação e atributos das exceções de domínio."""
    from src.domain.exceptions import ConfigurationError, RAGOrchestrationError, VectorStoreError, AgentInferenceError
    
    assert ConfigurationError("t").status_code == 500
    assert RAGOrchestrationError("t").status_code == 500
    assert VectorStoreError("t").status_code == 502
    assert AgentInferenceError("t").status_code == 502

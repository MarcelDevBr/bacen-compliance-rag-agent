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

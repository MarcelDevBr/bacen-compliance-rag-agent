"""
Módulo de testes automatizados para a camada de Domínio.

Valida a resiliência e as restrições estritas dos objetos de valor,
estruturas de dados e funções de inicialização da camada fundamental da Arquitetura Hexagonal.
"""

import pytest
from src.domain.config_loader import load_config
import os

def test_config_loader_not_found() -> None:
    """
    Testa a mecânica de restrição (Fail-Fast) do carregador de configuração.
    Espera-se o lançamento da exceção FileNotFoundError na ausência do arquivo base (config.yml).
    """
    with pytest.raises(FileNotFoundError):
        load_config(config_path="inexistente_123.yml")

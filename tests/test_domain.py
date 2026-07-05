import pytest
from src.domain.config_loader import load_config
import os

def test_config_loader_not_found():
    """Testa se o FileNotFoundError é lançado para config.yml inexistente."""
    with pytest.raises(FileNotFoundError):
        load_config(config_path="inexistente_123.yml")

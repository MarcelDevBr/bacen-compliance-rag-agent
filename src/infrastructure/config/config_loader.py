"""
Módulo de carregamento e validação de configurações.

Este módulo é responsável por ler o arquivo de configuração YAML e
converter seu conteúdo em estruturas fortemente tipadas utilizando Pydantic,
garantindo validação de esquema no momento da inicialização (fail-fast).
"""

import yaml
from dotenv import load_dotenv
from pathlib import Path
from src.domain.entities import AppConfig
from src.domain.messages import Messages

def load_config(config_path: str = "config.yml") -> AppConfig:
    """
    Carrega e valida o arquivo YAML de configuração.

    Args:
        config_path (str): Caminho para o arquivo de configuração YAML. Padrão é "config.yml".

    Returns:
        AppConfig: Instância contendo todas as configurações da aplicação validadas.

    Raises:
        FileNotFoundError: Se o arquivo especificado não for encontrado.
        pydantic.ValidationError: Se o conteúdo do YAML violar os esquemas definidos.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"{Messages.ERR_CONFIG_NOT_FOUND}: {config_path}")
        
    with open(path, "r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file)
        
    return AppConfig(**raw_config)

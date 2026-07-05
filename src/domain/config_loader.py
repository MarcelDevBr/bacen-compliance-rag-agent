import yaml
from pathlib import Path
from src.domain.models import AppConfig

def load_config(config_path: str = "config.yml") -> AppConfig:
    """
    Carrega e valida o arquivo YAML de configuração usando Pydantic.
    Garante falha rápida (fail-fast) se a configuração for inválida.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
    with open(path, "r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file)
        
    # O Pydantic fará o parse do dict e validará os tipos automaticamente (Zero verbosity)
    return AppConfig(**raw_config)

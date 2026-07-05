"""
Módulo adaptador para a interface da API Groq.

Implementa a lógica de instanciamento e injeção de dependências para o 
LLM fornecido pela Groq, isolando chaves de autenticação e detalhes de rede 
da camada de orquestração do LangChain.
"""

import os
from crewai import LLM
from src.infrastructure.config.config_loader import load_config
from src.domain.ports.llm_port import LLMPort

class LLMAdapter(LLMPort):
    """
    Classe adaptadora para o modelo de linguagem (LLM).
    
    Attributes:
        config (AppConfig): Modelos validados Pydantic contendo metadados do LLM.
        api_key (str): Chave de autorização criptografada injetada via ambiente.
    """
    def __init__(self) -> None:
        """
        Inicializa o adaptador processando as credenciais de segurança e parametrizações de modelo.

        Raises:
            ValueError: Se a variável de ambiente GROQ_API_KEY não estiver adequadamente provisionada.
        """
        self.config = load_config()
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "gsk_suachaveaqui":
            raise ValueError("GROQ_API_KEY não configurada corretamente no sistema operacional ou .env!")

    def get_client(self) -> LLM:
        """
        Provisiona e expõe o cliente LLM preparado para inferência pela CrewAI.

        Returns:
            LLM: Objeto cliente conectado à API externa com temperatura e modelo definidos via configuração.
        """
        return LLM(
            model=f"{self.config.llm.provider}/{self.config.llm.model_name}",
            temperature=self.config.llm.temperature,
            api_key=self.api_key
        )

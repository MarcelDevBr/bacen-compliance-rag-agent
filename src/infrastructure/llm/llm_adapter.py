"""
Módulo adaptador para a interface da API de LLM.

Implementa a lógica de instanciamento e injeção de dependências para o 
LLM fornecido (Groq ou Google Gemini), isolando chaves de autenticação e detalhes de rede 
da camada de orquestração do LangChain/CrewAI.
"""

import os
from crewai import LLM
from src.infrastructure.config.config_loader import load_config
from src.domain.ports.llm_port import LLMPort
from src.domain.entities import LLMProvider

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
        """
        self.config = load_config()
        
        if self.config.llm.provider == LLMProvider.GOOGLE:
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY não configurada no ambiente!")
        else:
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key or self.api_key == "gsk_suachaveaqui":
                raise ValueError("GROQ_API_KEY não configurada corretamente no sistema operacional ou .env!")

    def get_client(self) -> LLM:
        """
        Provisiona e expõe o cliente LLM preparado para inferência pela CrewAI.

        Returns:
            LLM: Objeto cliente conectado à API externa com temperatura e modelo definidos via configuração.
        """
        # LiteLLM prefix for Google Gemini is 'gemini/'
        provider_prefix = "gemini" if self.config.llm.provider == LLMProvider.GOOGLE else self.config.llm.provider
        
        return LLM(
            model=f"{provider_prefix}/{self.config.llm.model_name}",
            temperature=self.config.llm.temperature,
            api_key=self.api_key
        )

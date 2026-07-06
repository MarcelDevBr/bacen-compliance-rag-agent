"""
Módulo adaptador para a interface da API de LLM.

Implementa a lógica de instanciamento e injeção de dependências para o 
LLM fornecido (Groq ou Google Gemini), isolando chaves de autenticação e detalhes de rede 
da camada de orquestração do LangChain/CrewAI.
"""

import os
from crewai import LLM
from typing import Optional
from src.domain.ports.llm_port import LLMPort
from src.domain.entities import LLMProvider, AppConfig

class LLMAdapter(LLMPort):
    """
    Classe adaptadora para o modelo de linguagem (LLM).
    
    Attributes:
        config (AppConfig): Modelos validados Pydantic contendo metadados do LLM.
        api_key (str): Chave de autorização criptografada injetada via ambiente.
    """
    def __init__(self, config: AppConfig) -> None:
        """
        Inicializa o adaptador carregando chaves do ambiente.
        """
        self.config = config
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

    def get_client(self, provider_override: str | None = None) -> LLM:
        """
        Provisiona e expõe o cliente LLM preparado para inferência pela CrewAI.
        
        Args:
            provider_override (str, optional): Substitui o LLM padrão definido no config.yml.

        Returns:
            LLM: Objeto cliente conectado à API externa.
        """
        # Resolve o provedor: override tem preferência, depois config.yml
        provider = provider_override if provider_override else self.config.llm.provider
        
        if provider == LLMProvider.GOOGLE or provider == "google":
            if not self.gemini_key or self.gemini_key == "sua_chave":
                raise ValueError("GEMINI_API_KEY inválida ou não configurada.")
            provider_prefix = "gemini"
            model_name = "gemini-2.5-flash" if self.config.llm.provider != provider else self.config.llm.model_name
            api_key = self.gemini_key
        else:
            if not self.groq_key or self.groq_key == "gsk_suachaveaqui":
                raise ValueError("GROQ_API_KEY inválida ou não configurada.")
            provider_prefix = "groq"
            model_name = "llama3-70b-8192" if self.config.llm.provider != provider else self.config.llm.model_name
            api_key = self.groq_key
            
        return LLM(
            model=f"{provider_prefix}/{model_name}",
            temperature=self.config.llm.temperature,
            api_key=api_key
        )

"""
Módulo adaptador para a interface da API Groq.

Implementa a lógica de instanciamento e injeção de dependências para o 
LLM fornecido pela Groq, isolando chaves de autenticação e detalhes de rede 
da camada de orquestração do LangChain.
"""

import os
from langchain_groq import ChatGroq
from src.domain.config_loader import load_config

class LLMAdapter:
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

    def get_client(self) -> ChatGroq:
        """
        Provisiona e expõe o cliente LangChain preparado para inferência.

        Returns:
            ChatGroq: Objeto cliente conectado à API externa com temperatura e modelo definidos via configuração.
        """
        return ChatGroq(
            temperature=self.config.llm.temperature,
            model_name=self.config.llm.model_name,
            groq_api_key=self.api_key,
        )

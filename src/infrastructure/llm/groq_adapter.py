import os
from langchain_groq import ChatGroq
from src.domain.config_loader import load_config

class GroqAdapter:
    """
    Adapter Hexagonal para o LLM Groq.
    Retorna a instância do Langchain ChatGroq já configurada.
    """
    def __init__(self):
        self.config = load_config()
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "gsk_suachaveaqui":
            raise ValueError("GROQ_API_KEY não configurada corretamente no .env!")

    def get_client(self) -> ChatGroq:
        """Retorna o cliente ChatGroq pronto para uso com LangChain/CrewAI"""
        return ChatGroq(
            temperature=self.config.llm.temperature,
            model_name=self.config.llm.model_name,
            groq_api_key=self.api_key,
        )

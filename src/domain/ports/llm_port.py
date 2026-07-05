from abc import ABC, abstractmethod
from typing import Any

class LLMPort(ABC):
    """
    Interface (Port) primária para interação com Modelos de Linguagem (LLM).
    A camada de Domínio e Aplicação interagem com esta abstração em vez de classes concretas (ex: ChatGroq, OpenAI).
    """

    @abstractmethod
    def get_client(self) -> Any:
        """
        Retorna a instância do cliente configurado pronto para ser injetado.
        
        Returns:
            Any: Instância do LLM subjacente compatível com CrewAI/Langchain.
        """
        pass

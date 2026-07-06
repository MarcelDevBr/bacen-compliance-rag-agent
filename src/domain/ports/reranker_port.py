from abc import ABC, abstractmethod
from typing import List, Tuple
from src.domain.entities import Citation

class RerankerPort(ABC):
    """
    Porta (Interface) para serviços de Re-Ranking (Cross-Encoder ou Cohere).
    Garante o isolamento da regra de negócio (Application/Domain) da infraestrutura de ML.
    """
    
    @abstractmethod
    def rerank(self, query: str, documents: List[str], citations: List[Citation]) -> Tuple[List[str], List[Citation]]:
        """
        Reordena documentos baseados na semântica cruzada com a pergunta original.
        
        Args:
            query (str): Pergunta do usuário.
            documents (List[str]): Lista de textos recuperados previamente pelo Retriever.
            citations (List[Citation]): Lista de objetos Citation correspondentes aos documentos.
            
        Returns:
            Tuple[List[str], List[Citation]]: Retorna apenas os documentos mais relevantes e suas respectivas Citações atualizadas com novo score.
        """
        pass  # pragma: no cover

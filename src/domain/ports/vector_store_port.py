from abc import ABC, abstractmethod
from typing import Any, List

class VectorStorePort(ABC):
    """
    Interface (Port) primária para o Banco de Dados Vetorial.
    Assegura que a Aplicação desconheça a implementação concreta (ChromaDB, Pinecone, FAISS).
    """

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> tuple[List[str], List[Any]]:
        """
        Busca os k documentos mais semanticamente próximos à query.

        Args:
            query (str): A pergunta ou texto a ser pesquisado.
            top_k (int): Quantidade máxima de resultados a retornar.

        Returns:
            List[Any]: Lista contendo os fragmentos de texto retornados pelo banco vetorial.
        """
        pass  # pragma: no cover

    @abstractmethod
    def as_retriever(self) -> Any:
        """
        Retorna o recuperador (retriever) nativo para integração com a engine subjacente.
        """
        pass  # pragma: no cover

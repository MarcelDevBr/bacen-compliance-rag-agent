"""
Módulo adaptador para o banco de dados vetorial ChromaDB.

Implementa o padrão estrutural Adapter (Arquitetura Hexagonal), encapsulando
a lógica de inicialização, recuperação e persistência do ChromaDB,
desacoplando o domínio de negócios da infraestrutura de busca vetorial.
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from typing import Any, List

from src.domain.ports.vector_store_port import VectorStorePort
import logging

logger = logging.getLogger(__name__)

class VectorStoreAdapter(VectorStorePort):
    """
    Classe adaptadora para o sistema de busca vetorial (ChromaDB).
    
    Attributes:
        persist_dir (str): Diretório de persistência do índice no sistema de arquivos.
        collection_name (str): Nome da coleção no ChromaDB.
    """
    def __init__(self, persist_dir: str = "vector_store", collection_name: str = "bacen_collection") -> None:
        """
        Inicializa o cliente local do ChromaDB configurando diretórios de persistência.

        Args:
            persist_dir (str, optional): Caminho do diretório de armazenamento. Padrão é "vector_store".
            collection_name (str, optional): Nome da coleção. Padrão é "bacen_collection".
        """
        from llama_index.core import VectorStoreIndex
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        self.persist_dir = persist_dir
        self.collection_name = collection_name
        os.makedirs(persist_dir, exist_ok=True)
        self.db = chromadb.PersistentClient(path=persist_dir)
        
        logger.info(f"Conectando ao ChromaDB local: {self.persist_dir}")
        chroma_collection = self.db.get_or_create_collection(self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        logger.info("Carregando modelo de embeddings...")
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, embed_model=self.embed_model)
        self.retriever = self.index.as_retriever(similarity_top_k=5)
        
    def get_vector_store(self) -> ChromaVectorStore:
        """
        Recupera a instância ativa do VectorStore, provendo fallback para criação caso inexistente.

        Returns:
            ChromaVectorStore: Instância encapsulada pelo LlamaIndex pronta para Retrieval.
        """
        return self.vector_store

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        self.retriever.similarity_top_k = top_k
        nodes = self.retriever.retrieve(query)
        return [n.text for n in nodes[:top_k]]

    def as_retriever(self) -> Any:
        return self.retriever

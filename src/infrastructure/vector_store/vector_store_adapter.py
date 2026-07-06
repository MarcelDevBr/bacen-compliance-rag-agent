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
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import Any, List

from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.entities import AppConfig, Citation
import logging

logger = logging.getLogger(__name__)

class VectorStoreAdapter(VectorStorePort):
    """
    Classe adaptadora para o sistema de busca vetorial (ChromaDB).
    
    Attributes:
        persist_dir (str): Diretório de persistência do índice no sistema de arquivos.
        collection_name (str): Nome da coleção no ChromaDB.
    """
    def __init__(self, config: AppConfig) -> None:
        """
        Inicializa o cliente local do ChromaDB configurando diretórios de persistência.
        Os parâmetros (persist_dir, collection_name, embed_model) são injetados.
        """
        self.config = config
        self.persist_dir = self.config.rag.vector_store.persist_dir
        self.collection_name = self.config.rag.vector_store.collection_name
        os.makedirs(self.persist_dir, exist_ok=True)
        self.db = chromadb.PersistentClient(path=self.persist_dir)
        
        logger.info(f"Conectando ao ChromaDB local: {self.persist_dir}")
        chroma_collection = self.db.get_or_create_collection(self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        logger.info("Carregando modelo de embeddings...")
        self.embed_model = HuggingFaceEmbedding(model_name=self.config.rag.vector_store.embed_model)
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, embed_model=self.embed_model)
        self.retriever = self.index.as_retriever(similarity_top_k=self.config.rag.retriever.top_k)
        
    def get_vector_store(self) -> ChromaVectorStore:
        """
        Recupera a instância ativa do VectorStore, provendo fallback para criação caso inexistente.

        Returns:
            ChromaVectorStore: Instância encapsulada pelo LlamaIndex pronta para Retrieval.
        """
        return self.vector_store

    def search(self, query: str, top_k: int | None = None) -> tuple[List[str], List[Any]]:
        # Usa top_k passado via argumento, ou recorre ao top_k do config
        k_val = top_k if top_k is not None else self.config.rag.retriever.top_k
        retriever = self.index.as_retriever(similarity_top_k=k_val)
        nodes = retriever.retrieve(query)
        
        citations = []
        texts = []
        for n in nodes:
            content = n.node.get_content()
            texts.append(content)
            metadata = n.node.metadata or {}
            
            # Extract LlamaIndex PDF metadata
            file_name = metadata.get("file_name", "Desconhecido")
            page_label = metadata.get("page_label", "1")
            
            try:
                page_num = int(page_label)
            except ValueError:
                page_num = 1
                
            score = n.score if n.score is not None else 0.0
            
            citations.append(Citation(
                source_file=file_name,
                page_number=page_num,
                text_snippet=content[:200] + "...",
                relevance_score=round(score, 4)
            ))
            
        return texts, citations

    def as_retriever(self) -> Any:
        return self.retriever

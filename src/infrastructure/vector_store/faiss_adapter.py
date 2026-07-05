"""
Módulo adaptador para o banco de dados vetorial FAISS.

Este módulo implementa o padrão estrutural Adapter (Arquitetura Hexagonal), encapsulando
a lógica de inicialização, recuperação e persistência do FAISS (Facebook AI Similarity Search),
desacoplando o domínio de negócios da infraestrutura de busca vetorial.
"""

import faiss
import os
from llama_index.vector_stores.faiss import FaissVectorStore
import logging

logger = logging.getLogger(__name__)

class FaissDBAdapter:
    """
    Classe adaptadora para o sistema de busca de vizinhos mais próximos (FAISS).
    
    A substituição de ChromaDB para FAISS foi necessária visando a manutenção
    de compatibilidade estrita do Pydantic V1 sob o ambiente Python 3.14.6.
    
    Attributes:
        persist_dir (str): Diretório de persistência do índice no sistema de arquivos.
        persist_path (str): Caminho absoluto/relativo completo para o arquivo do índice.
        embedding_dim (int): Dimensionalidade latente do modelo de embedding utilizado 
                             (ex: 384 para 'all-MiniLM-L6-v2').
    """
    def __init__(self, persist_dir: str = "vector_store", embedding_dim: int = 384) -> None:
        """
        Inicializa o cliente local do FAISS configurando diretórios de persistência.

        Args:
            persist_dir (str, optional): Caminho do diretório de armazenamento. Padrão é "vector_store".
            embedding_dim (int, optional): Dimensão do vetor latente (Dense Vector). Padrão é 384.
        """
        self.persist_dir = persist_dir
        self.persist_path = os.path.join(persist_dir, "faiss_index.index")
        self.embedding_dim = embedding_dim
        os.makedirs(persist_dir, exist_ok=True)
        
    def get_vector_store(self) -> FaissVectorStore:
        """
        Recupera a instância ativa do VectorStore, provendo fallback para criação caso inexistente.

        Returns:
            FaissVectorStore: Instância encapsulada pelo LlamaIndex pronta para Retrieval.
        """
        if os.path.exists(self.persist_path):
            logger.info(f"Carregando FAISS do disco: {self.persist_path}")
            faiss_index = faiss.read_index(self.persist_path)
        else:
            logger.info(f"Criando novo índice FAISS com dimensão {self.embedding_dim}")
            faiss_index = faiss.IndexFlatL2(self.embedding_dim)
            
        return FaissVectorStore(faiss_index=faiss_index)
        
    def save(self, vector_store: FaissVectorStore) -> None:
        """
        Persiste o índice vetorial em disco (I/O operation).

        Args:
            vector_store (FaissVectorStore): Objeto ativo contendo o índice atualizado.
        """
        logger.info(f"Salvando índice FAISS em: {self.persist_path}")
        vector_store.client.write_index(self.persist_path)

import faiss
import os
from llama_index.vector_stores.faiss import FaissVectorStore
import logging

logger = logging.getLogger(__name__)

class FaissDBAdapter:
    def __init__(self, persist_dir: str = "vector_store", embedding_dim: int = 384):
        """
        Inicializa o cliente local do FAISS.
        FAISS foi escolhido devido à quebra de compatibilidade do ChromaDB (Pydantic V1)
        com a versão Python 3.14.6 exigida.
        
        O embedding 'all-MiniLM-L6-v2' gera vetores de tamanho 384.
        """
        self.persist_dir = persist_dir
        self.persist_path = os.path.join(persist_dir, "faiss_index.index")
        self.embedding_dim = embedding_dim
        os.makedirs(persist_dir, exist_ok=True)
        
    def get_vector_store(self) -> FaissVectorStore:
        """
        Retorna uma instância do FaissVectorStore, carregando do disco se existir,
        ou criando um novo índice L2.
        """
        if os.path.exists(self.persist_path):
            logger.info(f"Carregando FAISS do disco: {self.persist_path}")
            faiss_index = faiss.read_index(self.persist_path)
        else:
            logger.info(f"Criando novo índice FAISS com dimensão {self.embedding_dim}")
            faiss_index = faiss.IndexFlatL2(self.embedding_dim)
            
        return FaissVectorStore(faiss_index=faiss_index)
        
    def save(self, vector_store: FaissVectorStore):
        """Salva o índice no disco."""
        logger.info(f"Salvando índice FAISS em: {self.persist_path}")
        vector_store.client.write_index(self.persist_path)

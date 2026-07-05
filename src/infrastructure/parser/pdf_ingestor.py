"""
Módulo de ingestão e indexação vetorial.

Este script atua como o pipeline ETL (Extract, Transform, Load) do RAG,
responsável pelo particionamento heurístico (chunking) de documentos regulatórios (PDFs)
e persistência dos embeddings no banco vetorial.
"""

import os
import argparse
import logging
from pathlib import Path

# LlamaIndex Components
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Nossos módulos da Arquitetura Hexagonal
from src.infrastructure.config.config_loader import load_config
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_ingestion(data_dir: str) -> None:
    """
    Executa o pipeline de ingestão de documentos.

    Este método orquestra a leitura do diretório, parametrização do particionamento,
    Geração dos embeddings e a indexação final (HNSW/Flat) via LlamaIndex.

    Args:
        data_dir (str): Caminho absoluto ou relativo contendo os artefatos base (PDFs, TXTs).
    """
    logger.info("Iniciando Ingestão de Dados (ETL)...")
    
    # 1. Carrega a configuração (Fail-fast via Pydantic)
    config = load_config()
    logger.info(f"Configurações carregadas: Chunk Size={config.rag.chunk_size}, Overlap={config.rag.chunk_overlap}")

    # 2. Configura o modelo de Embedding local e gratuito (HuggingFace)
    # 'all-MiniLM-L6-v2' gera vetores de dimensão 384.
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    Settings.chunk_size = config.rag.chunk_size
    Settings.chunk_overlap = config.rag.chunk_overlap
    
    # IMPORTANTE: Desativamos a LLM padrão durante a ingestão
    Settings.llm = None 

    # 3. Lê os documentos da pasta
    path = Path(data_dir)
    if not path.exists() or not any(path.iterdir()):
        logger.error(f"O diretório {data_dir} não existe ou está vazio.")
        return

    logger.info(f"Lendo documentos de: {data_dir}")
    documents = SimpleDirectoryReader(data_dir).load_data()
    logger.info(f"{len(documents)} arquivos/páginas carregados com sucesso.")

    # 4. Inicializa o banco de dados vetorial ChromaDB
    db_adapter = VectorStoreAdapter()
    vector_store = db_adapter.get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 5. Executa o Chunking e Embedding e salva no FAISS
    logger.info("Criando os Chunks e gerando Embeddings (pode levar alguns segundos na primeira vez)...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        show_progress=True
    )
    logger.info("Ingestão concluída! Banco de dados vetorial (ChromaDB) populado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingestor de Normativas do Bacen")
    parser.add_argument("--input", type=str, default="data/normativas_bacen", help="Pasta com os PDFs/Textos")
    args = parser.parse_args()
    
    run_ingestion(data_dir=args.input)

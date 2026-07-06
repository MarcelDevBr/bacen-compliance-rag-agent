import logging
from typing import List, Tuple
from sentence_transformers import CrossEncoder

from src.domain.ports.reranker_port import RerankerPort
from src.domain.entities import Citation
from src.infrastructure.config.config_loader import load_config

logger = logging.getLogger(__name__)

class CrossEncoderRerankerAdapter(RerankerPort):
    """
    Adaptador de infraestrutura que utiliza a biblioteca sentence-transformers
    para instanciar um modelo Cross-Encoder local de Re-Ranking.
    """
    
    def __init__(self):
        """
        Carrega a configuração e os pesos da rede neural na memória (idealmente usado como Singleton).
        """
        config = load_config()
        self.model_name = config.rag.reranker.model_name
        self.top_n = config.rag.reranker.top_n
        
        logger.info(f"Carregando modelo Cross-Encoder ({self.model_name}) para Re-Ranking...")
        self.model = CrossEncoder(self.model_name)
        
    def rerank(self, query: str, documents: List[str], citations: List[Citation]) -> Tuple[List[str], List[Citation]]:
        if not documents:
            return [], []
            
        logger.info(f"Aplicando CrossEncoder Re-Ranking em {len(documents)} documentos...")
        
        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)
        
        # Zip, sort by score descending, take top_n
        top_pairs = sorted(zip(documents, citations, scores), key=lambda x: x[2], reverse=True)[:self.top_n]

        top_docs = [doc for doc, _, _ in top_pairs]
        top_citations = []

        # Atualiza os scores com o valor do reranker
        for _, cit, score in top_pairs:
            cit.relevance_score = round(float(score), 4)
            top_citations.append(cit)
            
        return top_docs, top_citations

import time
import logging
from fastapi import APIRouter, HTTPException
from src.domain.models import QueryRequest, RAGResponse, Citation
from src.application.graph import build_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Compliance"])

# Instancia o grafo globalmente (em produção seria ideal injetar isso)
rag_graph = build_graph()

@router.post("/query", response_model=RAGResponse, summary="Faz uma pergunta aos normativos do Bacen")
async def ask_compliance_question(request: QueryRequest):
    """
    Recebe uma pergunta do usuário (ex: Operador de CRM), envia para o LangGraph
    (que orquestra a recuperação no FAISS e o squad de Agentes LangChain) e 
    retorna a resposta auditada.
    """
    logger.info(f"Nova requisição recebida: {request.query}")
    start_time = time.time()
    
    try:
        # Prepara o estado inicial para o LangGraph
        initial_state = {
            "question": request.query,
            "thread_id": request.thread_id or "default",
            "documents": [],
            "citations": [],
            "final_answer": "",
            "messages": []
        }
        
        # Executa o grafo de agentes
        logger.info("Enviando requisição para o Pipeline LangGraph...")
        result = rag_graph.invoke(initial_state)
        
        # Opcional: Processar e mapear as fontes reais para a resposta
        # Neste MVP, criamos uma citação genérica apontando para o vetor base.
        citations = [
            Citation(
                source_file="mock_bacen_pix.txt (Banco Vetorial FAISS)",
                page_number=1,
                text_snippet="Documentos internos recuperados do normativo...",
                relevance_score=0.99
            )
        ]
        
        latency = int((time.time() - start_time) * 1000)
        
        return RAGResponse(
            answer=result["final_answer"],
            citations=citations,
            latency_ms=latency
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar a query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no processamento do agente.")

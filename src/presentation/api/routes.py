"""
Módulo de roteamento HTTP da API RESTful (FastAPI).

Este módulo define os endpoints expostos pela aplicação, mapeando requisições 
HTTP externas para a invocação da cadeia lógica subjacente do LangGraph (RAG).
"""

import time
import logging
from fastapi import APIRouter, HTTPException
from src.domain.entities import QueryRequest, ComplianceResponse, Citation
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.application.use_cases.rag_orchestrator import build_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Compliance"])

@router.post("/query", response_model=ComplianceResponse, summary="Processa uma consulta de compliance regulatório.")
async def ask_compliance_question(request: QueryRequest) -> ComplianceResponse:
    """
    Endpoint principal para processamento de inferências em linguagem natural.

    Recebe o payload do cliente, prepara o estado inicial da máquina de estado (LangGraph),
    orquestra a recuperação vetorial e invoca o Squad de Agentes para síntese da resposta.

    Args:
        request (QueryRequest): Payload validado contendo a string de busca e identificadores de sessão.

    Returns:
        ComplianceResponse: Objeto validado contendo a resposta gerada, metadados de latência e citações de fontes.

    Raises:
        HTTPException: Se ocorrer uma falha não mitigada no grafo de execução ou na camada de persistência.
    """
    logger.info(f"Nova requisição recebida: {request.query}")
    start_time = time.time()
    
    try:
        # Prepara o estado inicial para o LangGraph
        vector_port = VectorStoreAdapter()
        llm_port = LLMAdapter()
        rag_graph = build_graph(vector_store_port=vector_port, llm_port=llm_port)
        initial_state = {
            "question": request.query,
            "thread_id": request.thread_id or "default",
            "documents": [],
            "citations": [],
            "final_answer": "",
            "messages": []
        }
        
        # Invocação determinística do grafo de execução
        logger.info("Enviando requisição para o Pipeline LangGraph...")
        result = rag_graph.invoke(initial_state)
        
        # Mapeamento heurístico temporário de citações (A ser substituído por métricas reais de relevância LlamaIndex)
        citations = [
            Citation(
                source_file="mock_bacen_pix.txt (Banco Vetorial FAISS)",
                page_number=1,
                text_snippet="Documentos internos recuperados do normativo...",
                relevance_score=0.99
            )
        ]
        
        latency = int((time.time() - start_time) * 1000)
        
        return ComplianceResponse(
            answer=result["final_answer"],
            citations=citations,
            latency_ms=latency
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar a query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Falha sistêmica no processamento do agente orquestrador.")

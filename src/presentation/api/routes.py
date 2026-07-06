"""
Módulo de roteamento HTTP da API RESTful (FastAPI).

Este módulo define os endpoints expostos pela aplicação, mapeando requisições 
HTTP externas para a invocação da cadeia lógica subjacente do LangGraph (RAG).
"""

import time
import logging
from fastapi import APIRouter, Depends
from src.domain.entities import QueryRequest, ComplianceResponse, Citation, APIResponse
from src.domain.exceptions import RAGOrchestrationError
from src.domain.messages import Messages
from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.reranker_port import RerankerPort
from src.presentation.api.dependencies import get_vector_store, get_llm, get_reranker
from src.application.use_cases.rag_orchestrator import build_graph
from src.domain.security import mask_pii

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Compliance"])

@router.post("/query", response_model=APIResponse[ComplianceResponse], summary=Messages.ENDPOINT_QUERY_SUMMARY)
async def ask_compliance_question(
    request: QueryRequest,
    vector_port: VectorStorePort = Depends(get_vector_store),
    llm_port: LLMPort = Depends(get_llm),
    reranker_port: RerankerPort = Depends(get_reranker)
) -> APIResponse[ComplianceResponse]:
    """
    Endpoint principal para processamento de inferências em linguagem natural.

    Recebe o payload do cliente, prepara o estado inicial da máquina de estado (LangGraph),
    orquestra a recuperação vetorial e invoca o Squad de Agentes para síntese da resposta.
    """
    sanitized_query = mask_pii(request.query)
    logger.info(f"{Messages.LOG_NEW_REQUEST}: {sanitized_query}")
    start_time = time.time()
    
    # Prepara o estado inicial para o LangGraph
    rag_graph = build_graph(vector_store_port=vector_port, llm_port=llm_port, reranker_port=reranker_port)
    initial_state = {
        "question": sanitized_query,
        "thread_id": request.thread_id or "default",
        "documents": [],
        "citations": [],
        "final_answer": "",
        "messages": []
    }
    
    # Invocação determinística do grafo de execução
    logger.info(Messages.LOG_SENDING_TO_GRAPH)
    try:
        result = rag_graph.invoke(initial_state)
    except Exception as e:
        # Se ocorrer uma falha durante o invoke, subimos a exceção de domínio
        raise RAGOrchestrationError(f"{Messages.RAG_EXECUTION_FAILED}: {str(e)}")
    
    # Mapeamento real de citações retornadas pela etapa de Re-Ranking / Retrieval
    citations = result.get("citations", [])
    
    latency = int((time.time() - start_time) * 1000)
    
    compliance_response = ComplianceResponse(
        answer=result["final_answer"],
        citations=citations,
        latency_ms=latency
    )
    
    return APIResponse(
        success=True,
        data=compliance_response
    )

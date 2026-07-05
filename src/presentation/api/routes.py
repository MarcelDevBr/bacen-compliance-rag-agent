"""
Módulo de roteamento HTTP da API RESTful (FastAPI).

Este módulo define os endpoints expostos pela aplicação, mapeando requisições 
HTTP externas para a invocação da cadeia lógica subjacente do LangGraph (RAG).
"""

import time
import logging
from fastapi import APIRouter
from src.domain.entities import QueryRequest, ComplianceResponse, Citation, APIResponse
from src.domain.exceptions import RAGOrchestrationError
from src.domain.messages import Messages
from src.infrastructure.vector_store.vector_store_adapter import VectorStoreAdapter
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.application.use_cases.rag_orchestrator import build_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Compliance"])

@router.post("/query", response_model=APIResponse[ComplianceResponse], summary=Messages.ENDPOINT_QUERY_SUMMARY)
async def ask_compliance_question(request: QueryRequest) -> APIResponse[ComplianceResponse]:
    """
    Endpoint principal para processamento de inferências em linguagem natural.

    Recebe o payload do cliente, prepara o estado inicial da máquina de estado (LangGraph),
    orquestra a recuperação vetorial e invoca o Squad de Agentes para síntese da resposta.

    Args:
        request (QueryRequest): Payload validado contendo a string de busca e identificadores de sessão.

    Returns:
        APIResponse[ComplianceResponse]: Objeto padronizado contendo a resposta e citações.
    """
    logger.info(f"{Messages.LOG_NEW_REQUEST}: {request.query}")
    start_time = time.time()
    
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
    logger.info(Messages.LOG_SENDING_TO_GRAPH)
    try:
        result = rag_graph.invoke(initial_state)
    except Exception as e:
        # Se ocorrer uma falha durante o invoke, subimos a exceção de domínio
        raise RAGOrchestrationError(f"{Messages.RAG_EXECUTION_FAILED}: {str(e)}")
    
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
    
    compliance_response = ComplianceResponse(
        answer=result["final_answer"],
        citations=citations,
        latency_ms=latency
    )
    
    return APIResponse(
        success=True,
        data=compliance_response
    )

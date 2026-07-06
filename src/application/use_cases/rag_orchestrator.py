"""
Módulo de orquestração do LangGraph para o pipeline RAG.

Este módulo define os nós e as arestas do grafo acíclico direcionado (DAG) 
que governa o fluxo de dados desde a recepção da pergunta do usuário até 
a geração da resposta validada, integrando recuperação vetorial e avaliação multi-agente.
"""

import logging
from functools import partial
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.domain.entities import AppConfig
from src.domain.state import RAGState
from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.reranker_port import RerankerPort
from src.application.agents.compliance_agents import ComplianceSquad

logger = logging.getLogger(__name__)

def retrieve_node(state: RAGState, vector_store_port: VectorStorePort) -> dict:
    """
    Nó de processamento: Recupera documentos relevantes do índice vetorial.
    """
    question = state["question"]
    logger.info(f"LangGraph: Buscando contexto no Vector Store para a query: '{question}'")
    texts, citations = vector_store_port.search(question)
    return {"documents": texts, "citations": citations}

def rerank_node(state: RAGState, reranker_port: RerankerPort) -> dict:
    """
    Nó de processamento: Aplica Re-Ranking nos documentos recuperados.
    """
    question = state["question"]
    documents = state.get("documents", [])
    citations = state.get("citations", [])
    
    if not documents:
        return {}
        
    logger.info("LangGraph: Aplicando Re-Ranking nos documentos via RerankerPort...")
    top_docs, top_citations = reranker_port.rerank(question, documents, citations)
        
    return {"documents": top_docs, "citations": top_citations}

def generate_node(state: RAGState, llm_port: LLMPort, app_config: AppConfig) -> dict:
    """
    Nó de processamento: Gera e revisa a resposta usando o squad multi-agente.
    """
    logger.info("LangGraph: Iniciando geração de resposta com o Squad Multi-Agente...")
    context_str = "\n\n".join(state["documents"])
    provider = state.get("provider")
    
    squad = ComplianceSquad(llm_port=llm_port, config=app_config, provider_override=provider)
    final_answer: str = squad.run_squad(question=state["question"], retrieved_context=context_str)
    
    return {"final_answer": final_answer}

def build_graph(vector_store_port: VectorStorePort, llm_port: LLMPort, reranker_port: RerankerPort, app_config: AppConfig) -> CompiledStateGraph:
    """
    Constrói e compila a máquina de estado (StateGraph) do pipeline RAG utilizando Injeção de Dependência.
    """
    builder = StateGraph(RAGState)
    
    bound_retrieve = partial(retrieve_node, vector_store_port=vector_store_port)
    bound_rerank = partial(rerank_node, reranker_port=reranker_port)
    bound_generate = partial(generate_node, llm_port=llm_port, app_config=app_config)
    
    builder.add_node("retriever", bound_retrieve)
    builder.add_node("reranker", bound_rerank)
    builder.add_node("generator", bound_generate)
    
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "reranker")
    builder.add_edge("reranker", "generator")
    builder.add_edge("generator", END)
    
    return builder.compile()

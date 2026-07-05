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

from src.domain.entities import ComplianceResponse
from src.domain.state import RAGState
from src.infrastructure.config.config_loader import load_config
from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.llm_port import LLMPort
from src.application.agents.compliance_agents import ComplianceSquad

logger = logging.getLogger(__name__)

def retrieve_node(state: RAGState, vector_store_port: VectorStorePort) -> dict:
    """
    Nó de processamento: Recupera documentos relevantes do índice vetorial.
    """
    question = state["question"]
    logger.info(f"LangGraph: Buscando contexto no Vector Store para a query: '{question}'")
    results = vector_store_port.search(question, top_k=3)
    return {"documents": results}

def generate_node(state: RAGState, llm_port: LLMPort) -> dict:
    """
    Nó de processamento: Gera e revisa a resposta usando o squad multi-agente.
    """
    logger.info("LangGraph: Iniciando geração de resposta com o Squad Multi-Agente...")
    context_str = "\n\n".join(state["documents"])
    
    squad = ComplianceSquad(llm_port=llm_port)
    final_answer: ComplianceResponse = squad.run_squad(question=state["question"], retrieved_context=context_str)
    
    return {"final_answer": final_answer}

def build_graph(vector_store_port: VectorStorePort, llm_port: LLMPort) -> CompiledStateGraph:
    """
    Constrói e compila a máquina de estado (StateGraph) do pipeline RAG utilizando Injeção de Dependência.

    Args:
        vector_store_port (VectorStorePort): A interface (Port) injetada do banco vetorial.
        llm_port (LLMPort): A interface (Port) injetada de comunicação com o LLM.

    Returns:
        CompiledStateGraph: Uma instância compilada do grafo pronta para invocação.
    """
    builder = StateGraph(RAGState)
    
    # Usa functools.partial para injetar as portas (ports) nos nós
    bound_retrieve = partial(retrieve_node, vector_store_port=vector_store_port)
    bound_generate = partial(generate_node, llm_port=llm_port)
    
    builder.add_node("retriever", bound_retrieve)
    builder.add_node("generator", bound_generate)
    
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "generator")
    builder.add_edge("generator", END)
    
    return builder.compile()

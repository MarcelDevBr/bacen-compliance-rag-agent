"""
Módulo de orquestração do LangGraph para o pipeline RAG.

Este módulo define os nós e as arestas do grafo acíclico direcionado (DAG) 
que governa o fluxo de dados desde a recepção da pergunta do usuário até 
a geração da resposta validada, integrando recuperação vetorial e avaliação multi-agente.
"""

import logging
from langgraph.graph import StateGraph, START, END
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.domain.state import GraphState
from src.infrastructure.vector_store.chromadb_adapter import ChromaDBAdapter
from src.application.agents.compliance_agents import ComplianceAgents

logger = logging.getLogger(__name__)

def retrieve_node(state: GraphState) -> dict:
    """
    Nó de processamento: Recupera documentos relevantes do índice FAISS.

    Este nó executa a busca de documentos (Dense Retrieval) convertendo a pergunta
    do usuário em embeddings e consultando o banco vetorial.

    Args:
        state (GraphState): O estado atual da execução do grafo.

    Returns:
        dict: Um dicionário contendo a chave 'documents' com a lista de textos recuperados,
              que será mesclada ao estado global.
    """
    logger.info(f"LangGraph: Recuperando documentos para a pergunta: '{state['question']}'")
    
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db_adapter = ChromaDBAdapter()
    vector_store = db_adapter.get_vector_store()
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=2)
    
    nodes = retriever.retrieve(state["question"])
    documents = [n.text for n in nodes]
    return {"documents": documents}

def generate_node(state: GraphState) -> dict:
    """
    Nó de processamento: Gera e revisa a resposta usando o squad multi-agente.

    Este nó recebe os documentos recuperados no nó anterior e aciona a cadeia
    LangChain nativa (Analista + Revisor) para sintetizar uma resposta fundamentada.

    Args:
        state (GraphState): O estado atual da execução do grafo.

    Returns:
        dict: Um dicionário contendo a chave 'final_answer' com a resposta aprovada,
              que será mesclada ao estado global.
    """
    logger.info("LangGraph: Iniciando geração de resposta com o Squad Multi-Agente...")
    
    context_str = "\n\n".join(state["documents"])
    
    squad = ComplianceAgents()
    final_answer = squad.run_squad(question=state["question"], retrieved_context=context_str)
    
    return {"final_answer": final_answer}

def build_graph():
    """
    Constrói e compila a máquina de estado (StateGraph) do pipeline RAG.

    Returns:
        CompiledGraph: Uma instância compilada do grafo pronta para invocação (invoke).
    """
    builder = StateGraph(GraphState)
    
    builder.add_node("retriever", retrieve_node)
    builder.add_node("generator", generate_node)
    
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "generator")
    builder.add_edge("generator", END)
    
    return builder.compile()

import logging
from langgraph.graph import StateGraph, START, END
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.domain.state import GraphState
from src.infrastructure.vector_store.faiss_adapter import FaissDBAdapter
from src.application.agents.compliance_agents import ComplianceAgents

logger = logging.getLogger(__name__)

def retrieve_node(state: GraphState):
    """Nó do LangGraph: Recupera documentos relevantes do FAISS via LlamaIndex."""
    logger.info(f"LangGraph: Recuperando documentos para a pergunta: '{state['question']}'")
    
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db_adapter = FaissDBAdapter()
    vector_store = db_adapter.get_vector_store()
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=2)
    
    nodes = retriever.retrieve(state["question"])
    documents = [n.text for n in nodes]
    return {"documents": documents}

def generate_node(state: GraphState):
    """Nó do LangGraph: Chama o Squad Nativo (Analista + Revisor) para gerar a resposta."""
    logger.info("LangGraph: Iniciando geração de resposta com o Squad Multi-Agente...")
    
    context_str = "\n\n".join(state["documents"])
    
    squad = ComplianceAgents()
    final_answer = squad.run_squad(question=state["question"], retrieved_context=context_str)
    
    return {"final_answer": final_answer}

def build_graph():
    """Constrói e compila o StateGraph (Pipeline RAG)."""
    builder = StateGraph(GraphState)
    
    builder.add_node("retriever", retrieve_node)
    builder.add_node("generator", generate_node)
    
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "generator")
    builder.add_edge("generator", END)
    
    return builder.compile()

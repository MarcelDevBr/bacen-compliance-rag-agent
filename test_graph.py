import logging
import os
from src.application.graph import build_graph
from dotenv import load_dotenv

# Carrega a variável GROQ_API_KEY
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pipeline():
    logger.info("=== Iniciando Teste do RAG Multi-Agente (LangGraph + CrewAI) ===")
    
    # 1. Constrói o Grafo
    graph = build_graph()
    
    # 2. Prepara o input inicial (GraphState)
    initial_state = {
        "question": "Qual o prazo total para analisar e devolver o valor via Pix em caso de fraude?",
        "thread_id": "TICKET-123",
        "documents": [],
        "citations": [],
        "final_answer": "",
        "messages": []
    }
    
    # 3. Executa o fluxo (invoke)
    logger.info("Enviando pergunta para a IA...")
    result = graph.invoke(initial_state)
    
    # 4. Imprime o resultado final
    print("\n" + "="*50)
    print("PERGUNTA:", result["question"])
    print("RESPOSTA FINAL APROVADA PELO SQUAD:")
    print(result["final_answer"])
    print("="*50 + "\n")

if __name__ == "__main__":
    test_pipeline()

"""
Módulo de definição de estado para a orquestração via grafos.

Este módulo especifica a estrutura do estado global mantido pelo LangGraph
durante a execução da cadeia de recuperação e geração (RAG).
"""

from typing import TypedDict, List, Annotated
import operator
from src.domain.models import Citation

class GraphState(TypedDict):
    """
    Representação do estado global da execução no LangGraph.
    
    Attributes:
        question (str): A pergunta original formulada pelo usuário.
        thread_id (str): Identificador único da sessão/conversação, utilizado para memória contextual.
        documents (List[str]): Lista de trechos de documentos (chunks) recuperados na busca vetorial.
        citations (List[Citation]): Lista de objetos de citação rastreáveis associados aos documentos.
        final_answer (str): A resposta final consolidada e revisada pelos agentes.
        messages (Annotated[list, operator.add]): Histórico de mensagens da conversação, 
            anotado com a operação de concatenação (append) nativa do LangGraph.
    """
    question: str
    thread_id: str
    documents: List[str]
    citations: List[Citation]
    final_answer: str
    messages: Annotated[list, operator.add]

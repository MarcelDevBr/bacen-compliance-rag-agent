from typing import TypedDict, List, Annotated
import operator
from src.domain.models import Citation

class GraphState(TypedDict):
    """
    O estado global da Thread do LangGraph.
    Usando dict puro / TypedDict é o padrão ouro no LangGraph.
    """
    question: str
    thread_id: str
    documents: List[str]
    citations: List[Citation]
    final_answer: str
    
    # Exemplo de estado que permite "append" usando o operator.add
    messages: Annotated[list, operator.add]

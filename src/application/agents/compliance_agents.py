import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.infrastructure.llm.groq_adapter import GroqAdapter
from src.domain.config_loader import load_config

logger = logging.getLogger(__name__)

class ComplianceAgents:
    """
    Substitui a biblioteca CrewAI usando LangChain nativo puro,
    resolvendo a quebra de compatibilidade do Python 3.14.6 com o CrewAI (via ChromaDB interno).
    """
    def __init__(self):
        self.config = load_config()
        self.llm = GroqAdapter().get_client()

    def _execute_agent(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Executa um agente genérico (Chain) eliminando duplicação de código LCEL."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(kwargs)

    def run_analyst(self, question: str, retrieved_context: str) -> str:
        """Agente 1: Analista de Normativas"""
        logger.info("Agente Analista: Elaborando rascunho da resposta...")
        return self._execute_agent(
            self.config.prompts.analyst.system, 
            self.config.prompts.analyst.user, 
            question=question, 
            context=retrieved_context
        )

    def run_reviewer(self, draft: str, retrieved_context: str) -> str:
        """Agente 2: Auditor de Compliance"""
        logger.info("Agente Auditor: Revisando rascunho em busca de alucinações...")
        return self._execute_agent(
            self.config.prompts.reviewer.system, 
            self.config.prompts.reviewer.user, 
            draft=draft, 
            context=retrieved_context
        )

    def run_squad(self, question: str, retrieved_context: str) -> str:
        """Orquestra o squad."""
        draft = self.run_analyst(question, retrieved_context)
        return self.run_reviewer(draft, retrieved_context)

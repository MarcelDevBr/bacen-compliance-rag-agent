import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.infrastructure.llm.groq_adapter import GroqAdapter

logger = logging.getLogger(__name__)

class ComplianceAgents:
    """
    Substitui a biblioteca CrewAI usando LangChain nativo puro,
    resolvendo a quebra de compatibilidade do Python 3.14.6 com o CrewAI (via ChromaDB interno).
    """
    def __init__(self):
        self.llm = GroqAdapter().get_client()

    def run_analyst(self, question: str, retrieved_context: str) -> str:
        """Agente 1: Analista de Normativas"""
        logger.info("Agente Analista: Elaborando rascunho da resposta...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Você é um Analista de Normativas do Banco Central. Responda à dúvida do cliente baseando-se APENAS nos documentos fornecidos."),
            ("user", "PERGUNTA: {question}\n\nTEXTOS RECUPERADOS:\n{context}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"question": question, "context": retrieved_context})

    def run_reviewer(self, draft: str, retrieved_context: str) -> str:
        """Agente 2: Auditor de Compliance"""
        logger.info("Agente Auditor: Revisando rascunho em busca de alucinações...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Você é um Auditor-Chefe de Compliance extremamente chato e pragmático. Seu papel é revisar o Rascunho da Resposta e os Textos da Lei. Se o rascunho tiver informações (prazos, multas, regras) que NÃO constam na lei, corte-as imediatamente. Reescreva a resposta final de forma impecável, segura e amigável para o cliente."),
            ("user", "RASCUNHO:\n{draft}\n\nTEXTOS DA LEI (VERDADE ABSOLUTA):\n{context}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"draft": draft, "context": retrieved_context})

    def run_squad(self, question: str, retrieved_context: str) -> str:
        """Orquestra o squad."""
        draft = self.run_analyst(question, retrieved_context)
        final = self.run_reviewer(draft, retrieved_context)
        return final

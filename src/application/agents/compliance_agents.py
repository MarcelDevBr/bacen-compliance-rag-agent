"""
Módulo de definição dos Agentes de IA colaborativos (Squad) usando CrewAI.

Este módulo encapsula a lógica de orquestração de múltiplos agentes utilizando a biblioteca CrewAI.
O pipeline é modelado sob o paradigma de Reflection/Critique, onde um agente atua como elaborador 
e outro como validador de compliance regulatório.
"""

import logging
from crewai import Agent, Task, Crew, Process
from src.infrastructure.llm.llm_adapter import LLMAdapter
from src.domain.config_loader import load_config

logger = logging.getLogger(__name__)

class ComplianceAgents:
    """
    Classe orquestradora do squad de agentes de compliance utilizando CrewAI.
    
    Attributes:
        config (AppConfig): Instância contendo as configurações globais de domínio.
        llm (BaseChatModel): Cliente do Large Language Model inicializado via adaptador infraestrutural.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o squad carregando as parametrizações e instanciando a conexão com a API do LLM.
        """
        self.config = load_config()
        self.llm = LLMAdapter().get_client()

    def run_squad(self, question: str, retrieved_context: str) -> str:
        """
        Orquestra a execução da equipe (Analista seguido pelo Revisor) via CrewAI.

        Args:
            question (str): A pergunta original a ser respondida.
            retrieved_context (str): Evidência textual do banco de dados (ChromaDB).

        Returns:
            str: O artefato final validado.
        """
        logger.info("Iniciando Squad CrewAI (Analista -> Auditor)...")

        analyst_agent = Agent(
            role="Especialista em Normativas do Banco Central",
            goal=self.config.prompts.analyst.system,
            backstory="Você é um veterano em análises de normativos do Banco Central.",
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )

        reviewer_agent = Agent(
            role="Auditor-Chefe de Compliance",
            goal=self.config.prompts.reviewer.system,
            backstory="Você é um auditor rigoroso que pune alucinações matemáticas ou legais.",
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )

        draft_task = Task(
            description=self.config.prompts.analyst.user.format(question=question, context=retrieved_context),
            expected_output="Rascunho detalhado e técnico da resposta.",
            agent=analyst_agent
        )

        audit_task = Task(
            description=self.config.prompts.reviewer.user.format(draft="{draft_output}", context=retrieved_context),
            expected_output="Resposta final auditada e formatada em Markdown, sem alucinações.",
            agent=reviewer_agent
        )

        crew = Crew(
            agents=[analyst_agent, reviewer_agent],
            tasks=[draft_task, audit_task],
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        return str(result.raw if hasattr(result, "raw") else result)

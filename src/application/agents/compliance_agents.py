"""
Módulo de definição dos Agentes de IA colaborativos (Squad) usando CrewAI.

Este módulo encapsula a lógica de orquestração de múltiplos agentes utilizando a biblioteca CrewAI.
O pipeline é modelado sob o paradigma de Reflection/Critique, onde um agente atua como elaborador 
e outro como validador de compliance regulatório.
"""

import logging
from crewai import Agent, Task, Crew, Process
from src.domain.ports.llm_port import LLMPort
from src.domain.entities import AppConfig
from src.domain.messages import Messages

logger = logging.getLogger(__name__)

class ComplianceSquad:
    """
    Orquestra o esquadrão Multi-Agente (Analista e Auditor) especializado em normativos.
    
    Attributes:
        llm_port (LLMPort): Adaptador LLM injetado que respeita a interface (Port) do domínio.
    """
    
    def __init__(self, llm_port: LLMPort, config: AppConfig, provider_override: str | None = None) -> None:
        """
        Inicializa o squad carregando as parametrizações e instanciando a conexão com a API do LLM.
        """
        self.config = config
        self.llm = llm_port.get_client(provider_override=provider_override)

    def run_squad(self, question: str, retrieved_context: str) -> str:
        """
        Orquestra a execução da equipe (Analista seguido pelo Revisor) via CrewAI.

        Args:
            question (str): A pergunta original a ser respondida.
            retrieved_context (str): Evidência textual do banco de dados (ChromaDB).

        Returns:
            str: O artefato final validado.
        """
        logger.info(f"Iniciando Squad CrewAI (Analista -> Auditor) usando {self.llm.model}...")

        analyst_agent = Agent(
            role=Messages.ANALYST_ROLE,
            goal=self.config.prompts.analyst.system,
            backstory=Messages.ANALYST_BACKSTORY,
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )

        reviewer_agent = Agent(
            role=Messages.REVIEWER_ROLE,
            goal=self.config.prompts.reviewer.system,
            backstory=Messages.REVIEWER_BACKSTORY,
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )

        draft_task = Task(
            description=self.config.prompts.analyst.user.format(question=question, context=retrieved_context),
            expected_output=Messages.ANALYST_EXPECTED_OUTPUT,
            agent=analyst_agent
        )

        audit_task = Task(
            description=self.config.prompts.reviewer.user.format(draft="{draft_output}", context=retrieved_context),
            expected_output=Messages.REVIEWER_EXPECTED_OUTPUT,
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

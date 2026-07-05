"""
Módulo de definição dos Agentes de IA colaborativos (Squad) usando CrewAI.

Este módulo encapsula a lógica de orquestração de múltiplos agentes utilizando a biblioteca CrewAI.
O pipeline é modelado sob o paradigma de Reflection/Critique, onde um agente atua como elaborador 
e outro como validador de compliance regulatório.
"""

import logging
from crewai import Agent, Task, Crew, Process
from src.infrastructure.config.config_loader import load_config
from src.domain.ports.llm_port import LLMPort

logger = logging.getLogger(__name__)

class ComplianceSquad:
    """
    Orquestra o esquadrão Multi-Agente (Analista e Auditor) especializado em normativos.
    
    Attributes:
        llm_port (LLMPort): Adaptador LLM injetado que respeita a interface (Port) do domínio.
    """
    
    def __init__(self, llm_port: LLMPort) -> None:
        """
        Inicializa o squad carregando as parametrizações e instanciando a conexão com a API do LLM.
        """
        self.config = load_config()
        self.llm = llm_port.get_client()

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

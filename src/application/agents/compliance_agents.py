"""
Módulo de definição dos Agentes de IA colaborativos (Squad).

Este módulo encapsula a lógica de orquestração de múltiplos agentes utilizando a biblioteca
LangChain de forma nativa. O pipeline é modelado sob o paradigma de Reflection/Critique,
onde um agente atua como elaborador e outro como validador de compliance regulatório.
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.infrastructure.llm.groq_adapter import GroqAdapter
from src.domain.config_loader import load_config

logger = logging.getLogger(__name__)

class ComplianceAgents:
    """
    Classe orquestradora do squad de agentes de compliance.
    
    Substitui a biblioteca CrewAI usando construtos nativos (LCEL - LangChain Expression Language),
    solucionando problemas estruturais de compatibilidade com ambientes Python em versões extremas (edge releases).
    
    Attributes:
        config (AppConfig): Instância contendo as configurações globais de domínio.
        llm (BaseChatModel): Cliente do Large Language Model inicializado via adaptador infraestrutural.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o squad carregando as parametrizações e instanciando a conexão com a API do LLM.
        """
        self.config = load_config()
        self.llm = GroqAdapter().get_client()

    def _execute_agent(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Executa um agente genérico abstraindo a complexidade do LCEL.

        Args:
            system_prompt (str): A metainstrução principal definindo o comportamento (persona).
            user_prompt (str): O template do input do usuário, contendo placeholders.
            **kwargs: Dicionário contendo os valores que preencherão os placeholders no user_prompt.

        Returns:
            str: A string de saída formatada e processada pelo parser do modelo.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(kwargs)

    def run_analyst(self, question: str, retrieved_context: str) -> str:
        """
        Aciona o agente Analista de Normativas.

        Este agente é responsável por redigir um rascunho preliminar utilizando unicamente
        o contexto documental extraído.

        Args:
            question (str): A pergunta original submetida.
            retrieved_context (str): O texto extraído do banco vetorial.

        Returns:
            str: O rascunho da resposta formatado em string.
        """
        logger.info("Agente Analista: Elaborando rascunho da resposta...")
        return self._execute_agent(
            self.config.prompts.analyst.system, 
            self.config.prompts.analyst.user, 
            question=question, 
            context=retrieved_context
        )

    def run_reviewer(self, draft: str, retrieved_context: str) -> str:
        """
        Aciona o agente Auditor de Compliance.

        Este agente atua como validador (Critique), inspecionando o rascunho 
        para remover alucinações matemáticas ou invenções de regras não expressas na normativa.

        Args:
            draft (str): O rascunho gerado pelo agente Analista.
            retrieved_context (str): O texto extraído do banco vetorial, servindo de 'ground truth'.

        Returns:
            str: A resposta final, aprovada segundo métricas e heurísticas de compliance.
        """
        logger.info("Agente Auditor: Revisando rascunho em busca de alucinações...")
        return self._execute_agent(
            self.config.prompts.reviewer.system, 
            self.config.prompts.reviewer.user, 
            draft=draft, 
            context=retrieved_context
        )

    def run_squad(self, question: str, retrieved_context: str) -> str:
        """
        Orquestra a execução serializada de toda a equipe (Analista seguido pelo Revisor).

        Args:
            question (str): A pergunta original a ser respondida.
            retrieved_context (str): Evidência textual do banco de dados.

        Returns:
            str: O artefato final processado pelo agente Revisor.
        """
        draft = self.run_analyst(question, retrieved_context)
        return self.run_reviewer(draft, retrieved_context)

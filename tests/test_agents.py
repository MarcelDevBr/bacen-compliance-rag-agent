"""
Módulo de testes automatizados para a orquestração do CrewAI.

Este módulo isola o comportamento da biblioteca CrewAI, garantindo que
as parametrizações estritas de prompts e delegação sejam configuradas
corretamente antes da execução do kickoff.
"""

from unittest.mock import patch, MagicMock
from src.application.agents.compliance_agents import ComplianceSquad

@patch("src.application.agents.compliance_agents.Task")
@patch("src.application.agents.compliance_agents.Agent")
@patch("src.application.agents.compliance_agents.Crew")
def test_compliance_agents_run_squad(mock_crew_class, mock_agent, mock_task) -> None:
    """
    Testa a orquestração do Squad (Agentes Analista e Revisor) via CrewAI.
    A classe Crew é interceptada (mock), permitindo validar se a função `run_squad`
    retorna a saída estruturada simulada.
    """
    
    # Mock do objeto da equipe
    mock_crew_instance = MagicMock()
    
    # Simula o retorno de um objeto com .raw (comportamento padrão do CrewOutput no CrewAI)
    mock_result = MagicMock()
    mock_result.raw = "Final audited review by CrewAI"
    mock_crew_instance.kickoff.return_value = mock_result
    
    mock_crew_class.return_value = mock_crew_instance
    
    mock_llm_port = MagicMock()
    from tests.test_adapters import get_mock_config
    squad = ComplianceSquad(llm_port=mock_llm_port, config=get_mock_config())
    final_ans = squad.run_squad(question="Qual o SLA?", retrieved_context="O SLA é 30 minutos.")
    
    assert final_ans == "Final audited review by CrewAI"
    mock_crew_instance.kickoff.assert_called_once()

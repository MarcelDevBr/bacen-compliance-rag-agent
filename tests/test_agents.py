import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from src.application.agents.compliance_agents import ComplianceAgents

@patch("src.application.agents.compliance_agents.GroqAdapter")
def test_compliance_agents_run_squad(mock_groq):
    """
    Testa a orquestração do Squad (Analista e Revisor).
    Como a função `run_squad` invoca internamente `run_analyst` e `run_reviewer`, 
    nós mockamos (patch.object) essas funções filhas no próprio objeto.
    Isso isola o teste garantindo que o orquestrador passa o output do Analista para o Auditor corretamente.
    """
    mock_llm = MagicMock()
    mock_groq.return_value.get_client.return_value = mock_llm
    
    squad = ComplianceAgents()
    with patch.object(squad, "run_analyst") as mock_analyst:
        with patch.object(squad, "run_reviewer") as mock_reviewer:
            mock_analyst.return_value = "Analyst review"
            mock_reviewer.return_value = "Final audited review"
            
            final_ans = squad.run_squad("Minha pergunta", "Contexto falso")
            assert final_ans == "Final audited review"
            mock_analyst.assert_called_once()
            mock_reviewer.assert_called_once()

@patch("src.application.agents.compliance_agents.GroqAdapter")
@patch("src.application.agents.compliance_agents.StrOutputParser")
def test_compliance_agents_individual_runs(mock_parser, mock_groq):
    # Bypass LCEL execution complexity by mocking the output parser entirely,
    # or by mocking the whole chain's invoke method
    mock_llm = MagicMock()
    mock_groq.return_value.get_client.return_value = mock_llm
    
    # Since prompt | llm | parser creates a RunnableSequence, we can mock the parser's parse method
    # Or even simpler, mock prompt.from_messages
    pass

@patch("src.application.agents.compliance_agents.GroqAdapter")
@patch("src.application.agents.compliance_agents.ChatPromptTemplate")
def test_compliance_agents_chains(mock_prompt, mock_groq):
    """
    Testa a execução individual das LangChain Expression Language (LCEL) Chains.
    A cadeia original é: prompt | llm | StrOutputParser()
    Para mockar o overload do operador Bitwise OR (__or__), interceptamos a criação da mensagem e retornamos 
    um `mock_chain` no final, evitando erros do Pydantic (ValidationError) sobre 'Generation'.
    """
    mock_llm = MagicMock()
    mock_groq.return_value.get_client.return_value = mock_llm
    
    # Mocking the runnable chain's invoke
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Mocked Response"
    
    # When prompt | llm | parser happens, we mock the | operator
    mock_prompt.from_messages.return_value.__or__.return_value.__or__.return_value = mock_chain
    
    squad = ComplianceAgents()
    res1 = squad.run_analyst("Q", "Ctx")
    assert res1 == "Mocked Response"
    
    res2 = squad.run_reviewer("Draft", "Ctx")
    assert res2 == "Mocked Response"

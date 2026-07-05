class ComplianceRAGException(Exception):
    """Exceção base para o domínio do Compliance RAG."""
    pass

class LLMIntegrationError(ComplianceRAGException):
    """Levantada quando há falha na integração ou validação com o serviço de LLM."""
    pass

class VectorStoreIntegrationError(ComplianceRAGException):
    """Levantada quando há falha ao interagir com o Vector Store."""
    pass

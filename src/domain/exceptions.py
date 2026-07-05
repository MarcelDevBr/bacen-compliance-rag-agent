"""
Módulo de hierarquia de exceções de domínio.

Garante que todos os erros do sistema tenham semântica de negócios
antes de serem traduzidos para respostas HTTP na camada de apresentação.
"""

class BaseDomainException(Exception):
    """
    Exceção raiz para toda a regra de negócio e domínio.
    """
    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class ConfigurationError(BaseDomainException):
    """Lançada quando falha o carregamento de artefatos de configuração (ex: YAML, Env)."""
    def __init__(self, message: str):
        super().__init__(message, error_code="CONFIG_ERROR", status_code=500)

class RAGOrchestrationError(BaseDomainException):
    """Lançada quando a orquestração do LangGraph ou fluxo geral falha."""
    def __init__(self, message: str):
        super().__init__(message, error_code="ORCHESTRATION_ERROR", status_code=500)

class VectorStoreError(BaseDomainException):
    """Lançada quando a persistência ou recuperação do Vector DB falha."""
    def __init__(self, message: str):
        super().__init__(message, error_code="VECTOR_STORE_ERROR", status_code=502)

class AgentInferenceError(BaseDomainException):
    """Lançada quando falha a comunicação ou parse de saída do LLM/CrewAI."""
    def __init__(self, message: str):
        super().__init__(message, error_code="AGENT_INFERENCE_ERROR", status_code=502)

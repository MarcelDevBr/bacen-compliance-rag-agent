"""
Módulo de modelos de domínio e esquemas de configuração.

Este módulo concentra as definições de classes BaseModel do Pydantic,
que fornecem validação de tipos em tempo de execução para os dados da aplicação,
incluindo configurações (YAML) e interfaces de entrada/saída de API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class LLMConfig(BaseModel):
    """Esquema de configuração para provedores de Large Language Models."""
    provider: str = Field(default="groq", description="Nome do provedor LLM (ex: groq, google).")
    model_name: str = Field(default="llama3-70b-8192", description="Identificador do modelo a ser utilizado.")
    temperature: float = Field(default=0.1, description="Grau de aleatoriedade na geração de texto (0 a 1).")
    free_tier_mode: bool = Field(default=True, description="Sinaliza priorização de endpoints não tarifados.")

class RetrieverConfig(BaseModel):
    """Esquema de configuração para o componente de recuperação densa (Dense Retrieval)."""
    top_k: int = Field(default=5, description="Número de documentos base a serem recuperados na busca primária.")

class RerankerConfig(BaseModel):
    """Esquema de configuração para o componente de Re-Ranking (Cross-Encoder)."""
    enabled: bool = Field(default=True, description="Ativa a reordenação semântica dos documentos recuperados.")
    model_name: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", description="Modelo para Cross-Encoding.")
    top_n: int = Field(default=2, description="Número de documentos finais retidos após re-ranking.")

class RAGConfig(BaseModel):
    """Esquema de configuração agrupador do pipeline RAG."""
    chunk_size: int = Field(default=1000, description="Tamanho de cada bloco particionado durante a ingestão.")
    chunk_overlap: int = Field(default=200, description="Tamanho da sobreposição entre blocos particionados.")
    retriever: RetrieverConfig
    reranker: RerankerConfig

class TelemetryLangfuse(BaseModel):
    """Configurações específicas da plataforma de observabilidade Langfuse."""
    enabled: bool = Field(default=False, description="Ativa o rastreamento (tracing) de execuções no Langfuse.")

class TelemetryConfig(BaseModel):
    """Esquema agrupador para configurações de telemetria e observabilidade."""
    langfuse: TelemetryLangfuse

class AgentPromptConfig(BaseModel):
    """Esquema de metainstruções (prompts) individuais para agentes de IA."""
    system: str = Field(..., description="O system prompt estruturando as diretrizes do agente.")
    user: str = Field(..., description="O template de injeção de dados (variáveis independentes) do usuário.")

class PromptsConfig(BaseModel):
    """Esquema agrupador para instâncias de agentes do projeto."""
    analyst: AgentPromptConfig
    reviewer: AgentPromptConfig

class AppMetadata(BaseModel):
    """Esquema de metadados operacionais da aplicação."""
    name: str = Field(..., description="Nome de registro do aplicativo/serviço.")
    environment: str = Field(..., description="Ambiente de implantação (ex: production, staging, development).")

class AppConfig(BaseModel):
    """Raiz do esquema de configurações carregado a partir do YAML."""
    app: AppMetadata
    llm: LLMConfig
    rag: RAGConfig
    telemetry: TelemetryConfig
    prompts: PromptsConfig

# --- API Models ---
class QueryRequest(BaseModel):
    """Esquema do payload de entrada da requisição de inferência (Endpoint POST)."""
    query: str = Field(..., description="A pergunta do usuário final ou operador do CRM a ser respondida.")
    thread_id: Optional[str] = Field(None, description="Identificador da sessão para preservação de memória contextual (ex: ID de Ticket).")

class Citation(BaseModel):
    """Esquema representativo de uma fonte documental utilizada como evidência pela IA."""
    source_file: str = Field(..., description="Nome do artefato (ex: PDF) de origem da extração.")
    page_number: int = Field(..., description="Número da página indexada do documento fonte.")
    text_snippet: str = Field(..., description="Trecho literal extraído utilizado como base para a inferência.")
    relevance_score: float = Field(..., description="Grau de similaridade cosseno (ou re-rank score) do trecho.")

class RAGResponse(BaseModel):
    """Esquema do payload de saída da requisição de inferência (Endpoint POST)."""
    answer: str = Field(..., description="Resposta em formato texto/markdown validada pelos agentes.")
    citations: List[Citation] = Field(..., description="Vetor de citações extraídas garantindo XAI (Explainable AI).")
    latency_ms: int = Field(..., description="Métrica de observabilidade denotando tempo de resposta interno (milissegundos).")

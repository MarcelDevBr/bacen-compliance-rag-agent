from pydantic import BaseModel, Field
from typing import List, Optional

class LLMConfig(BaseModel):
    provider: str = Field(default="groq")
    model_name: str = Field(default="llama3-70b-8192")
    temperature: float = Field(default=0.1)
    free_tier_mode: bool = Field(default=True)

class RetrieverConfig(BaseModel):
    top_k: int = Field(default=5)

class RerankerConfig(BaseModel):
    enabled: bool = Field(default=True)
    model_name: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    top_n: int = Field(default=2)

class RAGConfig(BaseModel):
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    retriever: RetrieverConfig
    reranker: RerankerConfig

class TelemetryLangfuse(BaseModel):
    enabled: bool = Field(default=False)

class TelemetryConfig(BaseModel):
    langfuse: TelemetryLangfuse

class AgentPromptConfig(BaseModel):
    system: str
    user: str

class PromptsConfig(BaseModel):
    analyst: AgentPromptConfig
    reviewer: AgentPromptConfig

class AppMetadata(BaseModel):
    name: str
    environment: str

class AppConfig(BaseModel):
    app: AppMetadata
    llm: LLMConfig
    rag: RAGConfig
    telemetry: TelemetryConfig
    prompts: PromptsConfig

# --- API Models ---
class QueryRequest(BaseModel):
    query: str = Field(..., description="A pergunta do usuário ou do operador do CRM")
    thread_id: Optional[str] = Field(None, description="O ID da conversa (ex: Ticket do Zendesk) para memória de contexto")

class Citation(BaseModel):
    source_file: str
    page_number: int
    text_snippet: str
    relevance_score: float

class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    latency_ms: int

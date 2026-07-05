import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env) para o Groq API
load_dotenv()

from src.presentation.api.routes import router
from src.domain.config_loader import load_config

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega configuração global via Pydantic
app_config = load_config()

# Instancia a aplicação FastAPI
app = FastAPI(
    title=app_config.app.name,
    description="API REST robusta para o Agente de Compliance Regulatório do BACEN.",
    version="1.0.0"
)

# Adiciona CORS para permitir consumo pelo frontend (React/Vue/Angular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, usar lista de domínios restritos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os Endpoints (Roteador)
app.include_router(router)

@app.get("/", tags=["Health"])
def health_check():
    """Verifica se o servidor e as portas estão saudáveis."""
    return {
        "status": "online",
        "environment": app_config.app.environment,
        "message": "Sistema de Compliance Operacional. Acesso via /docs"
    }

# Instrução: Para rodar, use o comando:
# uv run uvicorn src.presentation.api.main:app --reload

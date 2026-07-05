"""
Módulo ponto-de-entrada (Entrypoint) da aplicação FastAPI.

Este módulo orquestra a subida do servidor ASGI, registrando rotas (endpoints),
middlewares (como CORS), e integrando o pipeline RAG à rede externa.
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.infrastructure.config.config_loader import load_config
from src.presentation.api.routes import router
from src.domain.exceptions import BaseDomainException
from src.domain.entities import APIResponse
from src.domain.messages import Messages

# Processamento de variáveis de ambiente do sistema operacional (.env)
load_dotenv()

# Inicialização de handlers de Logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validação do estado e hiperparâmetros de domínio
app_config = load_config()

app = FastAPI(
    title=app_config.app.name,
    description=Messages.API_DESCRIPTION,
    version="1.0.0"
)

# Acoplamento de middleware CORS visando intercomunicação via domínios distintos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # ADVERTÊNCIA: Substituir por lista estrita em ambiente de produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acoplamento do roteador de inferência principal
app.include_router(router)

@app.get("/", tags=["UI"], response_class=HTMLResponse)
def serve_ui() -> str:
    """
    Endpoint utilitário de provisionamento estático.

    Realiza a leitura do buffer do arquivo HTML que suporta o frontend (Chat),
    permitindo iteração rápida durante o ciclo de testes sem depender de CDNs.

    Returns:
        str: String literal formatada em HTML/CSS para renderização pelo navegador.
    """
    ui_path = os.path.join(os.path.dirname(__file__), "../ui/index.html")
    try:
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return Messages.UI_NOT_FOUND

@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Sonda de monitoramento de saúde do microsserviço (Liveness Probe).

    Essencial para orquestradores de contêineres (e.g. Kubernetes) determinarem
    a capacidade do pod de receber tráfego TCP.

    Returns:
        dict: Metadados operacionais sinalizando status e ambiente rodando.
    """
    return {
        "status": "online",
        "environment": app_config.app.environment,
        "message": Messages.SYSTEM_ONLINE
    }

@app.exception_handler(BaseDomainException)
async def domain_exception_handler(request: Request, exc: BaseDomainException):
    """
    Handler global para exceções de domínio controladas.
    Retorna uma resposta HTTP estruturada em JSON, e loga o erro formalmente.
    """
    logger.warning(f"Domain Exception [{exc.error_code}]: {exc.message}")
    
    response = APIResponse(
        success=False,
        error_message=exc.message,
        error_code=exc.error_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Fallback global para falhas não tratadas.
    Garante que erros inesperados também respeitem o contrato de APIResponse,
    evitando vazamento de rastreios sensíveis em Produção.
    """
    logger.error(f"Unhandled Exception at {request.url}: {str(exc)}", exc_info=True)
    
    response = APIResponse(
        success=False,
        error_message=Messages.INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR"
    )
    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )

"""
Módulo ponto-de-entrada (Entrypoint) da aplicação FastAPI.

Este módulo orquestra a subida do servidor ASGI, registrando rotas (endpoints),
middlewares (como CORS), e integrando o pipeline RAG à rede externa.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Processamento de variáveis de ambiente do sistema operacional (.env)
load_dotenv()

from pydantic import BaseModel, ValidationError
import logging
from src.infrastructure.config.config_loader import load_config
from src.presentation.api.routes import router

# Inicialização de handlers de Logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validação do estado e hiperparâmetros de domínio
app_config = load_config()

app = FastAPI(
    title=app_config.app.name,
    description="Interface de Programação de Aplicações (API) robusta para Compliance Regulatório (RAG).",
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
        return "<h1>Interface UI indisponível. Artefato HTML não alocado no diretório.</h1>"

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
        "message": "Sistema operacional estabilizado. Acesso à especificação OpenAPI via /docs"
    }

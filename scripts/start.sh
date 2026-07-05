#!/bin/bash
# Script para iniciar o servidor da API

echo "[*] Iniciando o servidor FastAPI (Porta 8000)..."
export PYTHONPATH=.
uv run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload

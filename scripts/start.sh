#!/bin/bash
# Script para iniciar o servidor da API

cd "$(dirname "$0")/.." || exit 1

echo "[*] Verificando status do servidor..."
PID=$(pgrep -f "uvicorn src.presentation.api.main:app")
if [ -n "$PID" ]; then
    echo "[-] O servidor já está rodando em background (PID: $PID)."
    echo "[-] Para ver os logs, execute ./scripts/status.sh"
    exit 0
fi

echo "[*] Iniciando o servidor FastAPI (Porta 8000)..."
mkdir -p logs
export PYTHONPATH=.
nohup uv run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/server.log 2>&1 &
NEW_PID=$!

echo "[+] Servidor iniciado em background (PID: $NEW_PID)."
echo "[+] Os logs estão sendo gravados em logs/server.log"
echo "[+] Para ver o status e os logs contínuos, execute: ./scripts/status.sh"

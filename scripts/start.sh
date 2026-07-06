#!/bin/bash
# Script para iniciar os servidores

cd "$(dirname "$0")/.." || exit 1

echo "[*] Verificando status dos servidores..."
PID_API=$(pgrep -f "uvicorn src.presentation.api.main:app")
PID_UI=$(pgrep -f "streamlit run frontend/app_streamlit.py")

if [ -n "$PID_API" ] || [ -n "$PID_UI" ]; then
    echo "[-] Os servidores já estão rodando."
    echo "[-] Para ver os logs, execute ./scripts/status.sh"
    exit 0
fi

API_PORT=${API_PORT:-8080}
UI_PORT=${UI_PORT:-8000}
API_HOST=${API_HOST:-0.0.0.0}

echo "[*] Iniciando o servidor FastAPI (Porta $API_PORT)..."
mkdir -p logs
export PYTHONPATH=.
nohup uv run uvicorn src.presentation.api.main:app --host $API_HOST --port $API_PORT --reload > logs/server.log 2>&1 &
API_PID=$!

echo "[*] Iniciando a interface Streamlit (Porta $UI_PORT)..."
nohup uv run streamlit run frontend/app_streamlit.py --server.port $UI_PORT --server.address $API_HOST > logs/ui.log 2>&1 &
UI_PID=$!

echo "[+] Servidores iniciados em background."
echo "    - FastAPI: PID $API_PID"
echo "    - Streamlit: PID $UI_PID"
echo "[+] Os logs estão sendo gravados em logs/server.log e logs/ui.log"
echo "[+] Acesse http://localhost:$UI_PORT para usar a interface."

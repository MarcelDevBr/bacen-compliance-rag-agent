#!/bin/bash
# Script para iniciar os servidores

cd "$(dirname "$0")/.." || exit 1

LOCK_API="logs/api.pid"
LOCK_UI="logs/ui.pid"

mkdir -p logs

echo "[*] Verificando status dos servidores..."
API_RUNNING=0
UI_RUNNING=0

if [ -f "$LOCK_API" ] && kill -0 $(cat "$LOCK_API") 2>/dev/null; then
    API_RUNNING=1
fi

if [ -f "$LOCK_UI" ] && kill -0 $(cat "$LOCK_UI") 2>/dev/null; then
    UI_RUNNING=1
fi

if [ "$API_RUNNING" -eq 1 ] || [ "$UI_RUNNING" -eq 1 ]; then
    echo "[-] Os servidores já estão rodando."
    echo "[-] Para ver os logs, execute ./scripts/status.sh"
    exit 0
fi

API_PORT=${API_PORT:-8080}
UI_PORT=${UI_PORT:-8000}
API_HOST=${API_HOST:-0.0.0.0}

echo "[*] Iniciando o servidor FastAPI (Porta $API_PORT)..."
export PYTHONPATH=.
nohup uv run uvicorn src.presentation.api.main:app --host $API_HOST --port $API_PORT --reload > logs/server.log 2>&1 &
API_PID=$!
echo $API_PID > "$LOCK_API"

echo "[*] Iniciando a interface Streamlit (Porta $UI_PORT)..."
nohup uv run streamlit run frontend/app_streamlit.py --server.port $UI_PORT --server.address $API_HOST > logs/ui.log 2>&1 &
UI_PID=$!
echo $UI_PID > "$LOCK_UI"

echo "[+] Servidores iniciados em background."
echo "    - FastAPI: PID $API_PID"
echo "    - Streamlit: PID $UI_PID"
echo "[+] Os logs estão sendo gravados em logs/server.log e logs/ui.log"
echo "[+] Acesse http://localhost:$UI_PORT para usar a interface."

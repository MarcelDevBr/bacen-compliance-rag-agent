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

echo "[*] Iniciando o servidor FastAPI (Porta 8080)..."
mkdir -p logs
export PYTHONPATH=.
nohup uv run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8080 --reload > logs/server.log 2>&1 &
API_PID=$!

echo "[*] Iniciando a interface Streamlit (Porta 8000)..."
nohup uv run streamlit run frontend/app_streamlit.py --server.port 8000 --server.address 0.0.0.0 > logs/ui.log 2>&1 &
UI_PID=$!

echo "[+] Servidores iniciados em background."
echo "    - FastAPI: PID $API_PID"
echo "    - Streamlit: PID $UI_PID"
echo "[+] Os logs estão sendo gravados em logs/server.log e logs/ui.log"
echo "[+] Acesse http://localhost:8000 para usar a interface."

#!/bin/bash
# Script para parar os servidores

cd "$(dirname "$0")/.." || exit 1

LOCK_API="logs/api.pid"
LOCK_UI="logs/ui.pid"

echo "[*] Parando o servidor FastAPI..."
if [ -f "$LOCK_API" ]; then
    PID=$(cat "$LOCK_API")
    kill $PID 2>/dev/null
    rm -f "$LOCK_API"
else
    pkill -f "uvicorn src.presentation.api.main:app"
fi

echo "[*] Parando a interface Streamlit..."
if [ -f "$LOCK_UI" ]; then
    PID=$(cat "$LOCK_UI")
    kill $PID 2>/dev/null
    rm -f "$LOCK_UI"
else
    pkill -f "streamlit run frontend/app_streamlit.py"
fi
echo "[+] Servidores parados com sucesso."

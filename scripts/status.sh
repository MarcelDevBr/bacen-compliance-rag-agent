#!/bin/bash
# Script para verificar o status dos servidores e imprimir os logs

cd "$(dirname "$0")/.." || exit 1

LOCK_API="logs/api.pid"
LOCK_UI="logs/ui.pid"

if [ -f "$LOCK_API" ] && kill -0 $(cat "$LOCK_API") 2>/dev/null; then
    PID_API=$(cat "$LOCK_API")
    echo "[+] FastAPI está RODANDO (PID: $PID_API)."
else
    PID_API=""
    echo "[-] FastAPI NÃO está rodando."
    rm -f "$LOCK_API" 2>/dev/null
fi

if [ -f "$LOCK_UI" ] && kill -0 $(cat "$LOCK_UI") 2>/dev/null; then
    PID_UI=$(cat "$LOCK_UI")
    echo "[+] Streamlit está RODANDO (PID: $PID_UI)."
else
    PID_UI=""
    echo "[-] Streamlit NÃO está rodando."
    rm -f "$LOCK_UI" 2>/dev/null
fi

echo ""
if [ -f "logs/server.log" ] && [ -f "logs/ui.log" ]; then
    if [ -n "$PID_API" ] || [ -n "$PID_UI" ]; then
        echo "[*] Exibindo os logs em tempo real (pressione Ctrl+C para sair):"
        tail -f logs/server.log logs/ui.log
    else
        echo "[*] Os serviços estão parados. Estes são os últimos logs registrados:"
        tail -n 15 logs/server.log logs/ui.log
    fi
else
    echo "[-] Arquivos de log não encontrados. Inicie o servidor primeiro."
fi

#!/bin/bash
# Script para verificar o status dos servidores e imprimir os logs

cd "$(dirname "$0")/.." || exit 1

PID_API=$(pgrep -f "uvicorn src.presentation.api.main:app")
PID_UI=$(pgrep -f "streamlit run frontend/app_streamlit.py")

if [ -n "$PID_API" ]; then
    echo "[+] FastAPI está RODANDO (PID: $PID_API)."
else
    echo "[-] FastAPI NÃO está rodando."
fi

if [ -n "$PID_UI" ]; then
    echo "[+] Streamlit está RODANDO (PID: $PID_UI)."
else
    echo "[-] Streamlit NÃO está rodando."
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

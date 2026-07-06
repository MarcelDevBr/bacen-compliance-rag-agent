#!/bin/bash
# Script para verificar o status do servidor e imprimir os logs

cd "$(dirname "$0")/.." || exit 1

PID=$(pgrep -f "uvicorn src.presentation.api.main:app")
if [ -n "$PID" ]; then
    echo "[+] O servidor está RODANDO (PID: $PID)."
else
    echo "[-] O servidor NÃO está rodando no momento."
fi

echo ""
if [ -f "logs/server.log" ]; then
    echo "[*] Exibindo os logs mais recentes (pressione Ctrl+C para sair):"
    tail -f logs/server.log
else
    echo "[-] Arquivo de log (logs/server.log) não encontrado. Inicie o servidor primeiro."
fi

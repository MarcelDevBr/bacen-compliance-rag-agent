#!/bin/bash
# Script para parar o servidor da API

echo "[*] Parando o servidor FastAPI..."
pkill -f "uvicorn src.presentation.api.main:app"
if [ $? -eq 0 ]; then
    echo "[+] Servidor parado com sucesso."
else
    echo "[-] Nenhum servidor rodando no momento."
fi

#!/bin/bash
# Script para parar os servidores

echo "[*] Parando o servidor FastAPI..."
pkill -f "uvicorn src.presentation.api.main:app"
echo "[*] Parando a interface Streamlit..."
pkill -f "streamlit run frontend/app_streamlit.py"
echo "[+] Servidores parados com sucesso."

#!/bin/bash
# Script para Teste Funcional (End-to-End)

echo "[*] Verificando a GEMINI_API_KEY no .env..."
cd "$(dirname "$0")/.." || exit 1
if grep -q "sua_chave" .env; then
    echo "[-] AVISO: A chave GEMINI_API_KEY no .env parece ser a chave de exemplo (sua_chave)."
    echo "[-] O teste funcional baterá na API real e vai falhar com erro de autenticação se a chave for inválida."
fi

API_PORT=${API_PORT:-8080}
API_HOST=${API_HOST:-0.0.0.0}

echo ""
echo "[*] Iniciando o servidor em background para teste funcional na porta $API_PORT..."
export PYTHONPATH=.
uv run uvicorn src.presentation.api.main:app --host $API_HOST --port $API_PORT &
SERVER_PID=$!

echo "[*] Aguardando o servidor subir (5 segundos)..."
sleep 5

echo "[*] Disparando requisição funcional de Teste para o Endpoint /api/v1/query..."
curl -s -X POST http://$API_HOST:$API_PORT/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "O que é o Mecanismo Especial de Devolução (MED)?"}' | uv run python -m json.tool

echo ""
echo "[*] Derrubando o servidor de testes (PID $SERVER_PID)..."
kill $SERVER_PID
echo "[+] Teste funcional finalizado."

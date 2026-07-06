#!/bin/bash
# Script para Teste Funcional (End-to-End)

echo "[*] Verificando a GEMINI_API_KEY no .env..."
cd "$(dirname "$0")/.." || exit 1
if grep -q "sua_chave" .env; then
    echo "[-] AVISO: A chave GEMINI_API_KEY no .env parece ser a chave de exemplo (sua_chave)."
    echo "[-] O teste funcional baterá na API real e vai falhar com erro de autenticação se a chave for inválida."
fi

echo ""
echo "[*] Iniciando o servidor em background para teste funcional..."
export PYTHONPATH=.
uv run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8080 &
SERVER_PID=$!

echo "[*] Aguardando o servidor subir (5 segundos)..."
sleep 5

echo "[*] Disparando requisição funcional de Teste para o Endpoint /api/v1/query..."
curl -s -X POST http://localhost:8080/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "O que é o Mecanismo Especial de Devolução (MED)?"}' | uv run python -m json.tool

echo ""
echo "[*] Derrubando o servidor de testes (PID $SERVER_PID)..."
kill $SERVER_PID
echo "[+] Teste funcional finalizado."

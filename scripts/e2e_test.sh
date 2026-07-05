#!/bin/bash
# Script para Teste Funcional (End-to-End)

echo "[*] Verificando a GROQ_API_KEY no .env..."
if grep -q "gsk_suachave" .env; then
    echo "[-] AVISO: A chave GROQ_API_KEY no .env parece ser a chave de exemplo (gsk_suachave)."
    echo "[-] O teste funcional baterá na API real da Groq e vai falhar com erro de autenticação se a chave for inválida."
fi

echo ""
echo "[*] Iniciando o servidor em background para teste funcional..."
export PYTHONPATH=.
uv run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "[*] Aguardando o servidor subir (5 segundos)..."
sleep 5

echo "[*] Disparando requisição funcional de Teste para o Endpoint /api/v1/query..."
curl -s -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "O que é o Mecanismo Especial de Devolução (MED)?"}' | uv run python -m json.tool

echo ""
echo "[*] Derrubando o servidor de testes (PID $SERVER_PID)..."
kill $SERVER_PID
echo "[+] Teste funcional finalizado."

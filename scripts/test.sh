#!/bin/bash
# Script para executar testes unitários

echo "[*] Executando suíte de testes unitários (pytest)..."
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=.
uv run pytest tests/ -v

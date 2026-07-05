#!/bin/bash
# Script para executar testes unitários

echo "[*] Executando suíte de testes unitários (pytest)..."
export PYTHONPATH=.
uv run pytest tests/ -v

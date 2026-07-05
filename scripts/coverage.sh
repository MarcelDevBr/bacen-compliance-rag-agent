#!/bin/bash
# Script para análise de cobertura (coverage)

echo "[*] Executando análise de cobertura de código..."
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=.
uv run pytest --cov=src tests/ --cov-report=term-missing

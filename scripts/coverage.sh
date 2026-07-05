#!/bin/bash
# Script para análise de cobertura (coverage)

echo "[*] Executando análise de cobertura de código..."
export PYTHONPATH=.
uv run pytest --cov=src tests/ --cov-report=term-missing

#!/bin/bash
# Script para realizar a ingestão de PDFs para o banco vetorial

echo "[*] Iniciando a ingestão de documentos PDF para o Vector Store..."
export PYTHONPATH=.
uv run src/infrastructure/parser/pdf_ingestor.py

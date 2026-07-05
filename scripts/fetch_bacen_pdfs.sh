#!/bin/bash
# Script para baixar PDFs de exemplo do BACEN para a pasta data/

mkdir -p data
echo "[*] Baixando documentos públicos e normativos para RAG..."

# URL 1: Cartilha Oficial do Pix (PDF Público do BCB)
echo "[1/2] Baixando Cartilha do Pix..."
curl -sL "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Cartilha_Pix.pdf" -o data/Cartilha_Pix_BCB.pdf
if [ $? -eq 0 ]; then
    echo "  [+] Sucesso!"
else
    echo "  [-] Falha no download."
fi

# URL 2: Um documento público genérico de resoluções de exemplo (para evitar bloqueios de firewall do BCB contra cURL, usamos um gerador de texto de teste caso necessário, mas vamos tentar um link governamental estável).
echo "[2/2] Baixando Relatório de Economia Bancária (Amostra de texto complexo)..."
curl -sL "https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2022.pdf" -o data/Relatorio_Economia_Bancaria.pdf
if [ $? -eq 0 ]; then
    echo "  [+] Sucesso!"
else
    echo "  [-] Falha no download."
fi

echo ""
echo "[*] Download concluído! Verifique a pasta 'data/'."
echo "[*] Lembre-se de rodar './scripts/ingest.sh' em seguida para que a Inteligência Artificial processe os novos arquivos."

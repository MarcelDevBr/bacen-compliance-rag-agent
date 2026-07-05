#!/usr/bin/env python
# Script para raspar (scrape) PDFs de resoluções e normativos públicos do BACEN

import requests
from bs4 import BeautifulSoup
import os
import time

def scrape_bacen():
    os.makedirs('data', exist_ok=True)
    print("[*] Iniciando web scraping dinâmico de normativos em bcb.gov.br (PDFs)...")
    
    # Utilizando DuckDuckGo HTML para encontrar PDFs indexados do domínio bcb.gov.br
    # Dork: site:bcb.gov.br ext:pdf resolucao
    url = "https://html.duckduckgo.com/html/?q=site:bcb.gov.br+ext:pdf+resolucao"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', class_='result__url'):
            href = a.get('href')
            if href:
                # DuckDuckGo HTML exibe a URL real na tag text (ou podemos parsear o link redirecionado)
                # Exemplo de texto: www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix.pdf
                actual_url = a.text.strip()
                if "bcb.gov.br" in actual_url.lower() and ".pdf" in actual_url.lower():
                    if not actual_url.startswith("http"):
                        actual_url = "https://" + actual_url
                    links.append(actual_url)
        
        # Deduplicação
        links = list(set(links))
        
        if not links:
            print("[-] Não foi possível encontrar PDFs estáticos no motor de busca.")
            print("[*] Vamos usar links estáticos de fallback garantidos do governo...")
            links = [
                "https://www.in.gov.br/en/web/dou/-/resolucao-bcb-n-1-de-12-de-agosto-de-2020-272747183/pdf",
                "https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2022.pdf"
            ]
        else:
            print(f"[+] Foram encontrados {len(links)} documentos PDF indexados.")
            
        print("[*] Baixando até 5 arquivos para a Base de Conhecimento...")
        
        for i, pdf_url in enumerate(links[:5]):
            print(f"  -> Baixando {pdf_url}...")
            try:
                pdf_res = requests.get(pdf_url, headers=headers, timeout=15)
                if pdf_res.status_code == 200:
                    filename = f"data/Bacen_Normativo_{i+1}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_res.content)
                    print(f"  [OK] Salvo como {filename}")
                else:
                    print(f"  [ERRO] HTTP {pdf_res.status_code}")
            except Exception as e:
                print(f"  [ERRO] {str(e)}")
            time.sleep(1) # Delay para evitar block (rate limiting)
            
        print("\n[*] Raspagem concluída! Verifique os PDFs na pasta 'data/' e execute o ./scripts/ingest.sh")
            
    except Exception as e:
        print(f"[-] Falha catastrófica no scraping: {str(e)}")

if __name__ == "__main__":
    scrape_bacen()

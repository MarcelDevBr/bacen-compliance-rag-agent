import json
import os
from src.presentation.api.main import app

def generate_docs():
    os.makedirs("docs", exist_ok=True)
    
    # Extrai o esquema OpenAPI
    openapi_schema = app.openapi()
    
    # Salva o openapi.json
    with open("docs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    # Gera o HTML do ReDoc estático apontando para o openapi.json local
    html = """<!DOCTYPE html>
<html>
<head>
    <title>ReDoc - BACEN Compliance RAG</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <redoc spec-url='openapi.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
</body>
</html>
"""
    with open("docs/redoc.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("[+] ReDoc estático gerado em docs/redoc.html e esquema em docs/openapi.json")

if __name__ == "__main__":
    generate_docs()

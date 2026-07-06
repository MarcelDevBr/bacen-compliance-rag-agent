# Usamos a imagem oficial do Python 3.14 (base slim para menor tamanho)
# Como o Python 3.14.6 ainda não tem release oficial final no Dockerhub, 
# podemos simular usando python:3.14-rc-slim ou python:3.13-slim (para segurança em prod)
FROM python:3.14-rc-slim

# Metadados
LABEL maintainer="Marcel <marcel.sa.br@gmail.com>"
LABEL description="API do BACEN Compliance RAG (FastAPI + LangGraph + FAISS)"

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala ferramentas do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o gerenciador de pacotes UV
RUN pip install uv

# Copia os arquivos de dependência primeiro (para usar cache de camadas do Docker)
COPY pyproject.toml .

# Instala as dependências usando UV (mais rápido que pip)
RUN uv venv && uv pip install -e .
RUN uv pip install fastapi uvicorn llama-index-embeddings-huggingface llama-index-vector-stores-faiss llama-index-readers-file faiss-cpu python-dotenv langchain-groq langgraph

# Copia o resto do código da aplicação
COPY . .

# Expõe a porta que a API vai rodar
EXPOSE 8000

# Comando para rodar a API usando uvicorn dentro do ambiente UV
CMD ["uv", "run", "uvicorn", "src.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

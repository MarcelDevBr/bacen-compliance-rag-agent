# 🏛️ BACEN Compliance RAG - Multi-Agent AI System

![Python 3.14](https://img.shields.io/badge/Python-3.14.6-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF9900)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)

Um sistema avançado de Inteligência Artificial para atuar como **Auditor e Analista de Compliance** com base em normativos do Banco Central do Brasil (BACEN). Projetado com foco em **Clean Code, Arquitetura Hexagonal e MLOps**, este projeto serve como prova de conceito.

---

## 🧠 Arquitetura do Sistema

O projeto foi construído seguindo os princípios da **Arquitetura Hexagonal** (Ports & Adapters), garantindo que a regra de negócios fique totalmente isolada das tecnologias externas.

* **Ingestão e Vetorização (ETL):** `LlamaIndex` + `HuggingFace (all-MiniLM-L6-v2)`. Embeddings gerados localmente, sem custos de API.
* **Banco de Dados Vetorial:** `FAISS` (Facebook AI Similarity Search) - implementado via Hot-Swap arquitetural para resolver quebras de dependência.
* **Orquestração e Memória:** `LangGraph`, atuando como o cérebro que roteia a query, busca no FAISS e chama o Squad de Agentes.
* **Squad Multi-Agente Nativo:** Desenvolvido puramente em `LangChain` (Agente Analista + Agente Auditor de Compliance) para garantir respostas 100% ancoradas na lei (anti-alucinação).
* **Camada de Apresentação:** `FastAPI` (REST JSON) e uma elegante interface Web UI nativa com Glassmorphism.
* **LLM Provider:** `Groq API` (Alta velocidade, custo zero) via modelo Llama-3.

## ⚠️ A Decisão Arquitetural (O Caso CrewAI vs Python 3.14 Edge)

Originalmente planejado para usar `CrewAI`, a equipe de engenharia identificou durante o *runtime* que a biblioteca `crewai` possuía uma dependência profunda com o `ChromaDB` (via `Pydantic V1`), que por sua vez tem a sintaxe depreciada e incompatível com a engine do **Python 3.14.6**.

**Solução Sênior:** Em vez de fazer *downgrade* do ambiente ou aceitar o vendor lock-in, aplicamos o *Design Pattern* do projeto hexagonal:

1. O *ChromaDB* foi extirpado e substituído de forma transparente pelo **FAISS**.
2. O *CrewAI* foi removido, e a orquestração Multi-Agente (Analista e Revisor) foi reconstruída de forma 100% nativa em `LangChain`. Nenhuma regra de negócio precisou ser alterada.

---

## 🚀 Como Executar Localmente

### Pré-requisitos

* Ter o [uv](https://github.com/astral-sh/uv) instalado.
* Obter uma chave gratuita na [Groq Cloud](https://console.groq.com/keys).

### Passo a Passo

1. **Clone e configure o ambiente**
   Copie o arquivo de variáveis de ambiente e insira sua chave da Groq:

   ```bash
   cp .env.example .env
   ```

2. **Ingestão de Dados (Criação do Banco Vetorial FAISS)**
   Popule o banco de dados lendo o Mock do BACEN (Pix):

   ```bash
   make ingest
   ```

   *(Ou: `uv run python -m src.infrastructure.parser.pdf_ingestor`)*

3. **Suba o Servidor FastAPI e a Interface Web**

   ```bash
   make run
   ```

   *(Ou: `uv run uvicorn src.presentation.api.main:app --reload`)*

4. **Teste a Interface**
   Abra seu navegador em **[http://localhost:8000/](http://localhost:8000/)** para acessar a elegante UI do Chat.
   Ou acesse **[http://localhost:8000/docs](http://localhost:8000/docs)** para o painel de desenvolvedor Swagger.

---

## 🐳 Como Executar via Docker (Day-2 Ops)

O projeto está pronto para Cloud (ex: Google Cloud Run). Para subir localmente via contêineres:

```bash
make docker-up
```

*(Ou: `docker-compose up --build`)*

---

## ✅ Qualidade e Testes (100% de Cobertura)

O projeto contém uma suíte de testes unitários super robusta (`pytest`), validando as regras de negócio, a infraestrutura (Mocks do FAISS e LLM Groq), orquestração (LangGraph) e endpoints (FastAPI). **A cobertura de código (Coverage) é de 100%**.

Para rodar os testes e gerar o relatório:

```bash
make test
# Ou: PYTHONPATH=. uv run pytest tests/ --cov=src --cov-report=term-missing
```

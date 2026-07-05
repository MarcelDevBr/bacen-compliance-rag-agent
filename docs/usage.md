# 📖 Manual de Uso (Usage Guide)

Bem-vindo ao sistema RAG de Compliance do BACEN! Este documento detalha como operar o sistema tanto via Interface Gráfica quanto via API programática.

## 1. Interface Web (UI)

A forma mais simples de utilizar o sistema é através da interface web que já acompanha o servidor FastAPI. Ela possui um design elegante (Glassmorphism) e é responsiva.

### Acessando
1. Inicie o servidor: `./scripts/start.sh`
2. Abra seu navegador em: [http://localhost:8000/](http://localhost:8000/)

### Operação
- Digite sua dúvida no campo inferior de chat. Exemplo: *"Qual é o limite de tempo para o estorno de um PIX segundo as normativas?"*
- O sistema informará que está "Consultando o Cérebro de IA...".
- **Atenção:** Como utilizamos agentes CrewAI baseados em arquitetura ReAct para maximizar a precisão, a resposta pode demorar alguns segundos, pois a IA consulta os documentos vetoriais, raciocina, delega tarefas entre o Analista e o Auditor, e então retorna a resposta final.

## 2. API Programática (REST JSON)

Você pode integrar o motor de Compliance em outros sistemas utilizando o endpoint `POST /ask`.

### Endpoint
- **URL:** `http://localhost:8000/ask`
- **Método:** `POST`
- **Headers:** `Content-Type: application/json`

### Body da Requisição
```json
{
  "question": "Como funciona o Mecanismo Especial de Devolução (MED)?"
}
```

### Exemplo via cURL
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "Qual é a penalidade para instituições que não cumprem o SLA do Pix?"}'
```

### Resposta (Response)
```json
{
  "answer": "De acordo com o Manual do Pix e as resoluções do BACEN, as instituições que não cumprirem o Acordo de Nível de Serviço (SLA) estão sujeitas a sanções..."
}
```

## 3. Consultando a Documentação da API

A documentação interativa e detalhada da API está disponível em dois formatos nativos:

1. **Swagger UI:** Acesse [http://localhost:8000/docs](http://localhost:8000/docs) com a aplicação rodando para testar os endpoints diretamente do navegador.
2. **ReDoc:** Acesse [http://localhost:8000/redoc](http://localhost:8000/redoc) (ou abra o arquivo local `docs/redoc.html`) para visualizar a documentação formal e os esquemas dos modelos (Pydantic).

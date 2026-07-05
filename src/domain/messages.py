"""
Módulo de centralização de mensagens e textos informativos.

Armazena as strings literais do sistema para facilitar manutenções
e permitir futura internacionalização (i18n).
"""

class Messages:
    # --- API Info ---
    API_DESCRIPTION = "Interface de Programação de Aplicações (API) robusta para Compliance Regulatório (RAG)."
    
    # --- Health & Status ---
    SYSTEM_ONLINE = "Sistema operacional estabilizado. Acesso à especificação OpenAPI via /docs"
    
    # --- UI ---
    UI_NOT_FOUND = "<h1>Interface UI indisponível. Artefato HTML não alocado no diretório.</h1>"
    
    # --- Erros Genéricos ---
    INTERNAL_SERVER_ERROR = "Ocorreu um erro interno inesperado no servidor."
    
    # --- RAG / Orchestration ---
    RAG_EXECUTION_FAILED = "Falha na execução do grafo RAG"

    # --- CrewAI Agents ---
    ANALYST_ROLE = "Especialista em Normativas do Banco Central"
    ANALYST_BACKSTORY = "Você é um veterano em análises de normativos do Banco Central."
    ANALYST_EXPECTED_OUTPUT = "Rascunho detalhado e técnico da resposta."
    
    REVIEWER_ROLE = "Auditor-Chefe de Compliance"
    REVIEWER_BACKSTORY = "Você é um auditor rigoroso que pune alucinações matemáticas ou legais."
    REVIEWER_EXPECTED_OUTPUT = "Resposta final auditada e formatada em Markdown, sem alucinações."

    # --- Logs & Cli ---
    LOG_NEW_REQUEST = "Nova requisição recebida"
    LOG_SENDING_TO_GRAPH = "Enviando requisição para o Pipeline LangGraph..."
    CLI_INGESTOR_DESC = "Ingestor de Normativas do Bacen"
    
    # --- Endpoints ---
    ENDPOINT_QUERY_SUMMARY = "Processa uma consulta de compliance regulatório."
    
    # --- Exceptions ---
    ERR_CONFIG_NOT_FOUND = "Arquivo de configuração não encontrado"

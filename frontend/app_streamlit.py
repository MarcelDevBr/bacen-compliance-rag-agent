import streamlit as st
import requests
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Bacen Compliance RAG",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para dar um ar mais corporativo/assertivo
st.markdown("""
<style>
    .reportview-container {
        background: #f4f6f9;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---- BARRA LATERAL ----
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Banco_Central_do_Brasil_logo.svg/2560px-Banco_Central_do_Brasil_logo.svg.png", width=150)
    st.title("Sistema de Compliance")
    st.markdown("Agente de Inteligência Artificial especializado na análise e auditoria de normativos oficiais do **Banco Central do Brasil**.")
    
    st.divider()
    
    st.subheader("🔗 Links para Desenvolvedores")
    st.markdown("""
    Acesse a documentação técnica da API (FastAPI) e o playground interativo:
    - 📚 [Swagger UI (Docs)](http://localhost:8080/docs)
    - 📖 [ReDoc (Especificação)](http://localhost:8080/redoc)
    - 🎮 [LangServe Playground](http://localhost:8080/rag/playground)
    """)
    
    st.divider()
    
    if st.button("🗑️ Limpar Histórico de Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br><small>Versão 1.1.0 | Engine: Google Gemini (Cross-Encoder Re-Ranked)</small>", unsafe_allow_html=True)


# ---- ÁREA PRINCIPAL ----
st.title("🏦 Bacen Compliance RAG")
st.markdown("Faça perguntas sobre regulamentos, circulares e manuais do BACEN. A IA retornará a resposta devidamente ancorada na legislação em vigor.")

API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1/query")

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Mensagem de boas-vindas do assistente
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Olá! Sou o seu Agente Especialista em Compliance do BACEN. Como posso auxiliar na análise normativa hoje?",
        "citations": None,
        "latency": None
    })

# Exibe histórico do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Se houver citações na mensagem, exibe em um expander elegante
        if message.get("citations"):
            with st.expander(f"⚖️ Ver Fontes Normativas ({len(message['citations'])} encontradas)"):
                for idx, cit in enumerate(message["citations"]):
                    st.markdown(f"**{idx+1}. {cit['source_file']} (Página {cit['page_number']})** - Relevância: `{cit['relevance_score']:.2f}`")
                    st.info(f"_{cit['text_snippet']}_")
        
        # Exibe a latência de forma sutil
        if message.get("latency"):
            st.caption(f"⏱️ Tempo de resposta: {message['latency']}ms")

# Captura nova pergunta
if prompt := st.chat_input("Ex: Qual o prazo máximo para a devolução do Pix via MED?"):
    # Exibe pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Exibe resposta do assistente (com spinner de carregamento)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("Analisando o repositório de normativos do BACEN..."):
                payload = {"query": prompt, "thread_id": "streamlit-session"}
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        answer = data["data"]["answer"]
                        citations = data["data"]["citations"]
                        latency = data["data"]["latency_ms"]
                        
                        # Mostra a resposta principal
                        message_placeholder.markdown(answer)
                        
                        # Mostra as citações e latência para a UI atual
                        with st.expander(f"⚖️ Ver Fontes Normativas ({len(citations)} encontradas)"):
                            for idx, cit in enumerate(citations):
                                st.markdown(f"**{idx+1}. {cit['source_file']} (Página {cit['page_number']})** - Relevância: `{cit['relevance_score']:.2f}`")
                                st.info(f"_{cit['text_snippet']}_")
                        st.caption(f"⏱️ Tempo de resposta: {latency}ms")
                        
                        # Salva no histórico para as próximas renderizações
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "citations": citations,
                            "latency": latency
                        })
                    else:
                        error_msg = f"Erro na IA de Compliance: {data.get('error_message')}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    message_placeholder.error(f"Erro de Conexão: HTTP {response.status_code}")
        except Exception as e:
            message_placeholder.error(f"O backend da API (porta 8080) parece estar offline. Detalhe: {e}")

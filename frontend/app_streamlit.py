import streamlit as st
import requests
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Bacen Compliance RAG",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Bacen Compliance RAG")
st.markdown("Assistente inteligente para normas do Banco Central.")

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/query")

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura nova pergunta
if prompt := st.chat_input("Como posso ajudar com o compliance normativo?"):
    # Adiciona pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Exibe resposta (com spinner de carregamento)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("Analisando normativos..."):
                payload = {"query": prompt, "thread_id": "streamlit-session"}
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        answer = data["data"]["answer"]
                        citations = data["data"]["citations"]
                        latency = data["data"]["latency_ms"]
                        
                        # Formata resposta com citações
                        full_response = f"{answer}\n\n---\n**Citações Extraídas:**\n"
                        for idx, cit in enumerate(citations):
                            full_response += f"**{idx+1}. {cit['source_file']} (Pág {cit['page_number']})** - Score: {cit['relevance_score']}\n"
                            full_response += f"> {cit['text_snippet']}\n\n"
                            
                        full_response += f"*(Latência: {latency}ms)*"
                        
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        error_msg = f"Erro na API: {data.get('error_message')}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    message_placeholder.error(f"Erro HTTP {response.status_code}")
        except Exception as e:
            message_placeholder.error(f"Falha de conexão com a API: {e}")

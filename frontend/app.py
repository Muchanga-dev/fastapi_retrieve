# -*- coding: utf-8 -*-
"""
Created on Sat May 11 16:12:59 2024

@author: mucha
"""
import streamlit as st
import requests
import json

# URL do endpoint
url = "http://localhost:8000/ask"

# Cabeçalhos da requisição
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Função principal do Streamlit
def main():
    st.title("Interface de Consulta")

    # Inicializar sessão de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensagens de chat existentes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Caixa de texto para entrada da pergunta
    if prompt := st.chat_input("Digite sua pergunta:"):
        st.session_state.messages.append({"role": "human", "content": prompt})
        with st.chat_message("human"):
            st.markdown(prompt)

        # Corpo da requisição com a pergunta do usuário
        payload = {
            "question": prompt
        }

        try:
            # Enviar a requisição POST
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # Verificar o status da resposta e conteúdo
            if response.status_code == 200:
                response_data = response.json()
                answer = response_data.get("context", {}).get("text", "Nenhuma resposta encontrada.")
                st.session_state.messages.append({"role": "ai", "content": answer})
                with st.chat_message("ai"):
                    st.markdown(answer)
            else:
                error_msg = f"Erro: {response.status_code}\n{response.text}"
                st.session_state.messages.append({"role": "ai", "content": error_msg})
                with st.chat_message("ai"):
                    st.markdown(error_msg)
        except Exception as e:
            error_msg = f"Ocorreu um erro ao se conectar com a API: {e}"
            st.session_state.messages.append({"role": "ai", "content": error_msg})
            with st.chat_message("ai"):
                st.markdown(error_msg)

if __name__ == "__main__":
    main()
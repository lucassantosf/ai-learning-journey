import streamlit as st
import re
import uuid
from streamlit_option_menu import option_menu
from src.agent.agent import Agent
from src.utils.helpers import get_products

# Modelos disponíveis
AVAILABLE_MODELS = ['gemini', 'openai', 'llama']

def initialize_state():
    if 'agent_model' not in st.session_state:
        st.session_state.agent_model = 'gemini'
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent(st.session_state.agent_model)
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}
    if 'current_chat' not in st.session_state:
        new_id = str(uuid.uuid4())
        st.session_state.current_chat = new_id
        st.session_state.chat_sessions[new_id] = []

def get_agent():
    if st.session_state.agent_model != st.session_state.get('last_model_used'):
        st.session_state.agent = Agent(st.session_state.agent_model)
        st.session_state.last_model_used = st.session_state.agent_model
    return st.session_state.agent

def get_current_chat_history():
    return st.session_state.chat_sessions[st.session_state.current_chat]

def add_message(role, content):
    st.session_state.chat_sessions[st.session_state.current_chat].append({"role": role, "content": content})

def display_chat_messages():
    for message in get_current_chat_history():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def detect_product_list(response):
    patterns = [r'Lista de Produtos:', r'Catálogo de Produtos:', r'Produtos Disponíveis:', r'Nossos Produtos:']
    for pattern in patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return re.findall(r'p\d{3}', response)
    return None

def header_controls():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### 🤖 Agente Simulado com IA")
    with col2:
        selected_model = st.selectbox(
            "Modelo",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(st.session_state.agent_model),
            key="model_selector",
            label_visibility="collapsed"
        )
        if selected_model != st.session_state.agent_model:
            st.session_state.agent_model = selected_model
            st.session_state.agent = Agent(selected_model)
            st.toast(f"Modelo alterado para: {selected_model}")

def sidebar_controls():
    with st.sidebar:
        if st.button("Novo chat"):
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = []
            st.session_state.current_chat = new_id

        st.title("Chats")

        chat_ids = list(st.session_state.chat_sessions.keys())
        chat_labels = [f"Conversa {chat_id[:8]}" for chat_id in chat_ids]

        selected_label = option_menu(
            menu_title=None,
            options=chat_labels,
            default_index=chat_ids.index(st.session_state.current_chat) if st.session_state.current_chat in chat_ids else 0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "#f0f2f6"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#ddd"},
                "nav-link-selected": {"background-color": "#0d6efd", "color": "white"},
            },
        )

        selected_index = chat_labels.index(selected_label)
        st.session_state.current_chat = chat_ids[selected_index]

        st.markdown("---")
        st.markdown(f"🔁 Modelo atual: **{st.session_state.agent_model}**")
        st.markdown(f"🆔 ID atual: `{st.session_state.current_chat[:8]}`")

def main():
    st.set_page_config(page_title="Agente Simulado", page_icon="🤖", layout="wide")

    initialize_state()
    sidebar_controls()
    header_controls()

    agent = get_agent()
    display_chat_messages()

    user_input = st.chat_input("Digite a tarefa que deseja que o agente realize")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        add_message("user", user_input)

        with st.chat_message("assistant"):
            with st.spinner("Executando..."):
                response = agent.call(user_input)
                st.markdown(response)

        add_message("assistant", response)

if __name__ == "__main__":
    main()

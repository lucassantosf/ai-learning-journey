import streamlit as st
import uuid
from src.agent.agent import Agent

AVAILABLE_MODELS = ['gemini', 'openai', 'llama']

def initialize_state():
    if 'agent_model' not in st.session_state:
        st.session_state.agent_model = 'gemini'
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent(st.session_state.agent_model)
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None  # Começa sem nenhum chat selecionado

def get_agent():
    if st.session_state.agent_model != st.session_state.get('last_model_used'):
        st.session_state.agent = Agent(st.session_state.agent_model)
        st.session_state.last_model_used = st.session_state.agent_model
    return st.session_state.agent

def get_current_chat_history():
    return st.session_state.chat_sessions[st.session_state.current_chat]["messages"]

def is_relevant_message(msg):
    return msg and msg.strip() and msg.lower().strip() not in ["oi", "olá", "bom dia", "boa noite", ""]

def add_message(role, content):
    # Se não existir chat, cria um agora
    if not st.session_state.current_chat:
        new_id = str(uuid.uuid4())
        st.session_state.current_chat = new_id
        st.session_state.chat_sessions[new_id] = {"messages": [], "has_content": False}

    chat = st.session_state.chat_sessions[st.session_state.current_chat]
    chat["messages"].append({"role": role, "content": content})
    if is_relevant_message(content):
        chat["has_content"] = True

def display_chat_messages():
    if not st.session_state.current_chat:
        return
    for message in get_current_chat_history():
        if message["role"] == "user":
            st.markdown(f"<div class='user-msg'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-msg'>{message['content']}</div>", unsafe_allow_html=True)

def header_controls():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("<h3 style='color:white;'>🤖 Agente Simulado com IA</h3>", unsafe_allow_html=True)
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
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #202123;
            padding: 0 10px;
        }
        .chat-item {
            padding: 10px 14px;
            margin: 4px 0;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-size: 15px;
            background-color: #202123;
            transition: background 0.2s ease;
            text-align: left;
        }
        .chat-item:hover {
            background-color: #2A2B32;
        }
        .chat-item-selected {
            background-color: #343541;
        }
        .sidebar-title {
            color: #FFFFFF;
            font-size: 16px;
            margin: 10px 0;
            font-weight: bold;
        }
        .new-chat-btn {
            width: 100%;
            background-color: #343541 !important;
            color: white !important;
            border: none !important;
            font-size: 15px !important;
            padding: 8px 0;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        .new-chat-btn:hover {
            background-color: #2A2B32 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        if st.button("➕ Novo chat", key="new_chat", use_container_width=True):
            current_chat = st.session_state.current_chat
            current_data = st.session_state.chat_sessions.get(current_chat)

            # Só cria novo se a conversa atual tiver conteúdo
            if current_chat is None or (current_data and current_data["has_content"]):
                new_id = str(uuid.uuid4())
                st.session_state.chat_sessions[new_id] = {"messages": [], "has_content": False}
                st.session_state.current_chat = new_id
                st.rerun()

        if st.session_state.chat_sessions:
            st.markdown("<div class='sidebar-title'>Chats</div>", unsafe_allow_html=True)

            chat_ids = list(st.session_state.chat_sessions.keys())
            for chat_id in chat_ids:
                label = f"Conversa {chat_id[:8]}"
                class_name = "chat-item"
                if chat_id == st.session_state.current_chat:
                    class_name += " chat-item-selected"

                if st.button(label, key=f"chat_{chat_id}", use_container_width=True):
                    current_chat = st.session_state.current_chat
                    current_data = st.session_state.chat_sessions.get(current_chat)

                    # Só deleta se for diferente da que vai selecionar e estiver vazia
                    if current_chat != chat_id and current_data and not current_data["has_content"]:
                        del st.session_state.chat_sessions[current_chat]

                    if chat_id in st.session_state.chat_sessions:
                        st.session_state.current_chat = chat_id
                    st.rerun()

def inject_dark_mode_css():
    st.markdown(
        """
        <style>
        body, [data-testid="stAppViewContainer"] {
            background-color: #343541 !important;
            color: white !important;
        }
        [data-testid="stHeader"] {background: none;}

        /* Sidebar fixa e sem resizer */
        [data-testid="stSidebar"] {
            background-color: #202123;
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
        }
        [data-testid="stSidebarResizer"] {
            display: none !important;
        }
        button[kind="header"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] + section {
            cursor: default !important;
        }

        div.stChatInput textarea {
            background-color: #40414F !important;
            color: white !important;
            border: 1px solid #555 !important;
        }

        .user-msg {
            background-color: #0D6EFD;
            color: white;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0;
            max-width: 80%;
            align-self: flex-end;
        }
        .assistant-msg {
            background-color: #444654;
            color: #E0E0E0;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0;
            max-width: 80%;
            align-self: flex-start;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def main():
    st.set_page_config(page_title="Agente Simulado", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

    inject_dark_mode_css()
    initialize_state()
    sidebar_controls()
    header_controls()

    agent = get_agent()
    display_chat_messages()

    user_input = st.chat_input("Digite a tarefa que deseja que o agente realize")
    if user_input:
        st.markdown(f"<div class='user-msg'>{user_input}</div>", unsafe_allow_html=True)
        add_message("user", user_input)

        with st.spinner("Executando..."):
            response = agent.call(user_input)
            st.markdown(f"<div class='assistant-msg'>{response}</div>", unsafe_allow_html=True)

        add_message("assistant", response)

if __name__ == "__main__":
    main()

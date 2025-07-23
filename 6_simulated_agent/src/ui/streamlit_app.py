import streamlit as st
from agent.agent import run_agent

def main():
    st.set_page_config(page_title="Agente Simulado", page_icon="🤖")
    st.title("🤖 Agente Simulado com IA")

    task = st.text_input("📝 Digite a tarefa que deseja que o agente realize:")

    if st.button("Executar tarefa"):
        with st.spinner("Executando..."):
            result = run_agent(task)
            st.success("✅ Resultado do agente:")
            st.write(result)

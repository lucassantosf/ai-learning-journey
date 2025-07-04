import streamlit as st
import json

st.set_page_config(page_title="Summarizer", layout="wide")

st.title("📚 Summarizer: Geração Automática de Resumos e Flashcards com IA")
st.write("Automatize seu aprendizado com resumos, perguntas e flashcards gerados por IA a partir de qualquer texto ou PDF.")

# ==============================
# Barra lateral com menu e configs
# ==============================
st.sidebar.header("🔷 Menu Principal")

menu = st.sidebar.radio(
    "Escolha o modo de uso:",
    ["📄 Upload de PDF", "📝 Inserir texto manualmente", "🔍 Perguntar sobre conteúdo"]
)

st.sidebar.header("🔧 Configurações")
chunk_size = st.sidebar.slider("Tamanho do chunk (tokens)", min_value=100, max_value=1000, value=500, step=50)
num_questions = st.sidebar.slider("Quantidade de perguntas/flashcards", min_value=1, max_value=20, value=5)
if st.sidebar.button("🔄 Resetar tudo"):
    st.experimental_rerun()

# ==============================
# Área principal
# ==============================

# 2️⃣ Seção de upload ou entrada de texto
content = None

if menu == "📄 Upload de PDF":
    uploaded_file = st.file_uploader("Envie um PDF com o conteúdo de estudo", type=["pdf"])
    if uploaded_file is not None:
        # Aqui você extrairia o texto do PDF (simulação):
        content = f"Conteúdo simulado extraído do arquivo: {uploaded_file.name}"
        st.success(f"PDF '{uploaded_file.name}' carregado com sucesso!")
elif menu == "📝 Inserir texto manualmente":
    content = st.text_area("Cole ou digite o conteúdo que deseja estudar", height=300)
elif menu == "🔍 Perguntar sobre conteúdo":
    user_question = st.text_input("Digite sua pergunta sobre o conteúdo:")
    if st.button("🔎 Responder"):
        # Simulação de resposta gerada
        st.write(f"Resposta simulada para a pergunta: **{user_question}**")
    st.stop()  # Não processa mais nada se o modo for "Perguntar sobre conteúdo"

# 3️⃣ Botão de ação para gerar materiais de estudo
if content:
    if st.button("📚 Gerar materiais de estudo"):
        with st.spinner("Gerando materiais com IA..."):
            # ====== Simulação do processamento ======
            summary = f"Resumo simulado do conteúdo (tamanho: {len(content)} caracteres)."
            questions = [
                {"question": f"Pergunta {i+1} simulada?", "answer": f"Resposta {i+1} simulada."}
                for i in range(num_questions)
            ]
            flashcards = [
                {"front": q["question"], "back": q["answer"]}
                for q in questions
            ]
            # ====== Fim do placeholder ======

            # 4️⃣ Resultado principal
            st.subheader("✅ Materiais Gerados")
            
            with st.expander("📌 Resumo do conteúdo"):
                st.write(summary)

            with st.expander("❓ Perguntas para revisão"):
                for q in questions:
                    st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

            with st.expander("🃏 Flashcards gerados"):
                for f in flashcards:
                    st.markdown(f"**Frente:** {f['front']}  \n**Verso:** {f['back']}")
            
            # 5️⃣ Exportação
            export_data = {
                "summary": summary,
                "questions": questions,
                "flashcards": flashcards
            }
            export_json = json.dumps(export_data, ensure_ascii=False, indent=2)

            st.download_button(
                label="⬇️ Baixar materiais em JSON",
                data=export_json,
                file_name="materiais_estudo.json",
                mime="application/json"
            )

            # CSV export simplificado (flashcards front/back)
            csv_data = "front,back\n" + "\n".join([f'"{f["front"]}","{f["back"]}"' for f in flashcards])
            st.download_button(
                label="⬇️ Exportar flashcards para Anki (CSV)",
                data=csv_data,
                file_name="flashcards.csv",
                mime="text/csv"
            )
            st.success("Materiais gerados com sucesso!")

# 6️⃣ Rodapé
st.markdown("---")
st.caption("Desenvolvido por XXX. Powered by LLMs & Streamlit.") 
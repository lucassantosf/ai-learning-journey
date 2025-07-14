import streamlit as st
import json
from src.pipelines.pdf_pipeline import process_pdf_file
from src.pipelines.rag_pipeline import RAG
from src.pipelines.summarizer import Summarizer
from src.core.chunking import TextChunker

def main():
    st.set_page_config(page_title="Summarizer", layout="wide")

    # Persistência da sessão
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = RAG()
    rag_system = st.session_state.rag_system

    if "summarizer" not in st.session_state:
        st.session_state.summarizer = Summarizer()
    summarizer = st.session_state.summarizer

    st.title("📚 Summarizer: Geração Automática de Resumos e Flashcards com IA")
    st.write("Automatize seu aprendizado com resumos, perguntas e flashcards gerados por IA a partir de qualquer texto ou PDF.")

    st.sidebar.header("🔷 Menu Principal")
    menu = st.sidebar.radio(
        "Escolha o modo de uso:",
        ["📄 Upload de PDF", "📝 Inserir texto manualmente", "🔍 Perguntar sobre conteúdo"]
    )

    st.sidebar.header("🔧 Configurações")
    num_questions = st.sidebar.slider("Quantidade de perguntas/flashcards", min_value=3, max_value=7, value=5)

    if st.sidebar.button("🔄 Resetar tudo"):
        st.session_state.clear()
        st.experimental_rerun()

    # ======================
    # Upload de PDF
    # ======================
    if menu == "📄 Upload de PDF":
        pdf_file = st.file_uploader("Envie um PDF com o conteúdo de estudo", type=["pdf"])

        if pdf_file is not None:
            with st.spinner("Processando PDF..."):
                try:
                    chunks = process_pdf_file(pdf_file)
                    rag_system.add_documents(chunks)
                    full_text = " ".join(chunk["text"] for chunk in chunks)
                    st.session_state.full_text = full_text  # salvar para outras abas

                    st.success(f"✅ PDF '{pdf_file.name}' carregado com {len(chunks)} chunks.")
                except Exception as e:
                    st.error(f"❌ Erro ao processar PDF: {str(e)}")

            with st.spinner("Gerando resumo e perguntas..."):
                try:
                    summary = summarizer.generate_summary(full_text)
                    st.subheader("📌 Resumo:")
                    st.write(summary)

                    questions = summarizer.generate_questions(full_text, num_questions)
                    st.subheader("❓ Perguntas geradas:")
                    for q in questions:
                        st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

                except Exception as e:
                    st.error(f"❌ Erro ao gerar materiais: {str(e)}")

    # ======================
    # Inserir texto manual
    # ======================
    elif menu == "📝 Inserir texto manualmente":
        content = st.text_area("Cole ou digite o conteúdo", height=300)

        if st.button("Processar texto"):
            if content:
                with st.spinner("Processando texto..."):
                    chunks = TextChunker().create_chunks(content, source="manual_input")
                    rag_system.add_documents(chunks)
                    st.session_state.full_text = content

                    summary = summarizer.generate_summary(content)
                    st.subheader("📌 Resumo:")
                    st.write(summary)

                    questions = summarizer.generate_questions(content, num_questions)
                    st.subheader("❓ Perguntas geradas:")
                    for q in questions:
                        st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")
            else:
                st.error("⚠️ Por favor, insira algum texto.")

    # ======================
    # Perguntar sobre conteúdo
    # ======================
    elif menu == "🔍 Perguntar sobre conteúdo":
        user_question = st.text_input("Digite sua pergunta:")

        if st.button("🔎 Responder"):
            if user_question:
                with st.spinner("Buscando resposta..."):
                    try:
                        response = rag_system.query_and_respond(user_question, n_results=1)
                        st.subheader("✅ Resposta encontrada:")
                        st.write(response)
                    except Exception as e:
                        st.error(f"❌ Erro ao buscar resposta: {str(e)}")
            else:
                st.warning("⚠️ Digite uma pergunta.")

    st.markdown("---")
    st.caption("Desenvolvido por XXX. Powered by LLMs & Streamlit.")

if __name__ == "__main__":
    main()

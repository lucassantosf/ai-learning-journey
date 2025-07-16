import streamlit as st
import io
from streamlit_mic_recorder import mic_recorder

from src.pipelines.pdf_pipeline import process_pdf_file
from src.pipelines.rag_pipeline import RAG
from src.pipelines.summarizer import Summarizer
from src.core.chunking import TextChunker
from src.services.transcription_service import TranscriptionService

def init_session_state():
    st.session_state.setdefault("rag_system", RAG())
    st.session_state.setdefault("summarizer", Summarizer())
    st.session_state.setdefault("transcription", TranscriptionService())

def handle_pdf_upload():
    st.header("📄 Upload de PDF")
    pdf_file = st.file_uploader("Envie um PDF com o conteúdo de estudo", type=["pdf"])

    if pdf_file:
        with st.spinner("Processando PDF..."):
            try:
                chunks = process_pdf_file(pdf_file)
                st.session_state.rag_system.add_documents(chunks)
                full_text = " ".join(chunk["text"] for chunk in chunks)
                st.session_state.full_text = full_text

                st.success(f"✅ PDF '{pdf_file.name}' carregado com {len(chunks)} chunks.")
            except Exception as e:
                st.error(f"❌ Erro ao processar PDF: {str(e)}")
                return

        with st.spinner("Gerando resumo e perguntas..."):
            summarizer = st.session_state.summarizer
            try:
                summary = summarizer.generate_summary(full_text)
                st.subheader("📌 Resumo:")
                st.write(summary)

                num_questions = st.session_state.num_questions
                questions = summarizer.generate_questions(full_text, num_questions)
                st.subheader("❓ Perguntas geradas:")
                for q in questions:
                    st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")
            except Exception as e:
                st.error(f"❌ Erro ao gerar resumo e perguntas: {str(e)}")

def handle_manual_text():
    st.header("📝 Inserir texto manualmente")
    content = st.text_area("Cole ou digite o conteúdo", height=300)

    if st.button("Processar texto"):
        if not content.strip():
            st.error("⚠️ Por favor, insira algum texto.")
            return

        with st.spinner("Processando texto..."):
            rag_system = st.session_state.rag_system
            summarizer = st.session_state.summarizer

            chunks = TextChunker().create_chunks(content, source="manual_input")
            rag_system.add_documents(chunks)
            st.session_state.full_text = content

            summary = summarizer.generate_summary(content)
            st.subheader("📌 Resumo:")
            st.write(summary)

            num_questions = st.session_state.num_questions
            questions = summarizer.generate_questions(content, num_questions)
            st.subheader("❓ Perguntas geradas:")
            for q in questions:
                st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

def handle_question_answering():
    st.header("🔍 Perguntar sobre conteúdo")

    # Inicializar sessão para pergunta e transcrição
    st.session_state.setdefault("user_question", "")
    st.session_state.setdefault("transcript", "")

    # Input de texto
    user_question = st.text_input(
        "Digite sua pergunta (ou grave sua voz):",
        value=st.session_state.user_question,
        key="user_question_input"
    )

    # Gravação de áudio
    audio_data = mic_recorder(
        start_prompt="🔴 Falar",
        stop_prompt="✅ Parar",
        key="mic_recorder"
    )

    if audio_data:
        st.success("Áudio gravado!")
        st.audio(audio_data['bytes'], format="audio/wav")

        with st.spinner("Transcrevendo áudio..."):
            transcription_service = st.session_state.transcription
            try:
                transcript = transcription_service.transcribe(io.BytesIO(audio_data['bytes']))
                st.session_state.transcript = transcript
                st.session_state.user_question = transcript  # atualiza o campo de pergunta
                st.success("Transcrição concluída!")
            except Exception as e:
                st.error(f"❌ Erro na transcrição: {e}")

    # Exibir transcrição se existir
    if st.session_state.transcript:
        st.markdown(f"**Transcrição:**\n```\n{st.session_state.transcript}\n```")

    if st.button("🔎 Obter resposta"):
        user_question = st.session_state.user_question.strip()
        if not user_question:
            st.warning("⚠️ Digite ou fale uma pergunta primeiro.")
            return

        with st.spinner("Consultando IA..."):
            try:
                rag_system = st.session_state.rag_system
                response = rag_system.query_and_respond(user_question, n_results=1)
                st.session_state.response = response
                st.success("✅ Resposta encontrada!")
            except Exception as e:
                st.error(f"❌ Erro ao buscar resposta: {str(e)}")

    # Exibir resposta sem sumir durante rerenderização
    if "response" in st.session_state:
        st.subheader("✅ Resposta encontrada:")
        st.write(st.session_state.response)

def main():
    st.set_page_config(page_title="Summarizer", layout="wide")

    init_session_state()

    st.title("📚 Summarizer: Aprenda com IA")
    st.write("Gere resumos, perguntas e consulte conteúdos com IA (texto, PDF ou voz).")

    # Sidebar
    st.sidebar.header("🔷 Menu Principal")
    menu = st.sidebar.radio(
        "Escolha o modo de uso:",
        ["📄 Upload de PDF", "📝 Inserir texto manualmente", "🔍 Perguntar sobre conteúdo"]
    )

    st.sidebar.header("🔧 Configurações")
    st.session_state.num_questions = st.sidebar.slider(
        "Quantidade de perguntas/flashcards", min_value=3, max_value=7, value=5
    )

    if st.sidebar.button("🔄 Resetar tudo"):
        st.session_state.clear()
        st.experimental_rerun()

    if menu == "📄 Upload de PDF":
        handle_pdf_upload()
    elif menu == "📝 Inserir texto manualmente":
        handle_manual_text()
    elif menu == "🔍 Perguntar sobre conteúdo":
        handle_question_answering()

    st.markdown("---")
    st.caption("Desenvolvido por XXX. Powered by LLMs & Streamlit")

if __name__ == "__main__":
    main()
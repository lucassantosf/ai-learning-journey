import streamlit as st
import io
from streamlit_mic_recorder import mic_recorder

# Assumindo que essas importações funcionam corretamente
from src.pipelines.pdf_pipeline import process_pdf_file
from src.pipelines.rag_pipeline import RAG
from src.pipelines.summarizer import Summarizer
from src.core.chunking import TextChunker
from src.services.transcription_service import TranscriptionService

def init_session_state():
    st.session_state.setdefault("rag_system", RAG())
    st.session_state.setdefault("summarizer", Summarizer())
    st.session_state.setdefault("transcription", TranscriptionService())

    st.session_state.setdefault("user_question_text", "")
    st.session_state.setdefault("input_key_counter", 0)
    st.session_state.setdefault("response", "")

    st.session_state.setdefault("audio_to_process", None)
    st.session_state.setdefault("processing_audio_step", "")
    st.session_state.setdefault("last_processed_audio_hash", None)
    st.session_state.setdefault("ready_to_query", False)

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


# Função para processar a pergunta (texto ou áudio)
def process_query_and_get_response(query_text: str):
    if not query_text.strip():
        st.toast("⚠️ Por favor, digite ou grave uma pergunta válida.")
        st.session_state.response = ""
        st.session_state.user_question_text = ""
        return

    st.session_state.response = "" # Limpa a resposta anterior antes de consultar

    spinner_placeholder_ai = st.empty() 
    with spinner_placeholder_ai.container():
        st.info("Consultando IA...") 

    try:
        rag = st.session_state.rag_system
        response = rag.query_and_respond(query_text, n_results=1)
        st.session_state.response = response
        st.toast("✅ Resposta gerada!")
    except Exception as e:
        st.error(f"❌ Erro ao buscar resposta: {e}")
        st.session_state.response = f"Não foi possível obter uma resposta: {e}"
    finally:
        spinner_placeholder_ai.empty() # Remove o spinner da IA

# Callback para o input de texto (acionado ao digitar e pressionar Enter)
def on_text_input_submit():
    query = st.session_state[f"user_question_input_{st.session_state.input_key_counter}"].strip()

    if query:
        st.session_state.audio_to_process = None
        st.session_state.processing_audio_step = ""
        st.session_state.last_processed_audio_hash = None
        st.session_state.response = ""
        process_query_and_get_response(query)
        st.session_state.user_question_text = ""  # Limpa input após enviar
        st.session_state.input_key_counter += 1   # Atualiza o key para limpar o input visualmente
    else:
        st.toast("⚠️ Por favor, digite uma pergunta válida.")

def handle_Youtubeing():
    st.header("🔍 Perguntar sobre conteúdo")

    col1, col2 = st.columns([9, 1])

    with col1:
        st.text_input(
            "Digite sua pergunta ou grave sua voz (pressione Enter para perguntar):",
            value=st.session_state.user_question_text,
            key=f"user_question_input_{st.session_state.input_key_counter}",
            on_change=on_text_input_submit
        )

    with col2:
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="✅", key="mic_recorder")

    # Processar áudio se tiver novo áudio
    if audio_data and audio_data.get('bytes') and not st.session_state.get("processing_audio_step"):
        current_hash = hash(audio_data["bytes"])
        if current_hash != st.session_state.last_processed_audio_hash:
            st.session_state.audio_to_process = audio_data['bytes']
            st.session_state.processing_audio_step = "transcribing"
            st.session_state.last_processed_audio_hash = current_hash
            st.rerun()

    # Transcrição do áudio
    if st.session_state.processing_audio_step == "transcribing":
        st.toast("🎙️ Transcrevendo áudio...")
        st.audio(st.session_state.audio_to_process, format="audio/wav")
        with st.spinner("Transcrevendo..."):
            try:
                transcript = st.session_state.transcription.transcribe(io.BytesIO(st.session_state.audio_to_process))
                st.toast("✅ Transcrição concluída!")

                st.session_state.user_question_text = transcript
                st.session_state.input_key_counter += 1

                # 🔑 Acionamos este flag para disparar a IA após o rerun
                st.session_state.ready_to_query = True

                st.session_state.processing_audio_step = ""
                st.session_state.audio_to_process = None

                st.rerun()

            except Exception as e:
                st.error(f"Erro transcrevendo: {e}")
                st.session_state.processing_audio_step = ""
                st.session_state.audio_to_process = None

    # ✅ Após a transcrição, consulta automática da IA
    if st.session_state.ready_to_query:
        query = st.session_state.user_question_text
        process_query_and_get_response(query)
        st.session_state.user_question_text = ""
        st.session_state.ready_to_query = False
        st.session_state.input_key_counter += 1
        st.rerun()

    # Exibição da resposta
    if st.session_state.response:
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
        handle_Youtubeing()

    st.markdown("---")
    st.caption("Desenvolvido por XXX. Powered by LLMs & Streamlit")

if __name__ == "__main__":
    main()
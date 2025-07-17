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
    
    st.session_state.setdefault("user_question_text", "") # Conteúdo atual do text_input
    st.session_state.setdefault("response", "")
    st.session_state.setdefault("text_input_key_counter", 0) # Para forçar a atualização do text_input

    # Novo estado para controlar o áudio
    st.session_state.setdefault("audio_to_process", None) # Armazena os bytes do áudio se houver
    st.session_state.setdefault("processing_audio_step", "") # 'transcribing', 'querying_ai', ''
    # Guarda o hash do áudio para saber se é um áudio novo ou o mesmo que já foi processado
    st.session_state.setdefault("last_processed_audio_hash", None) 

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
    current_text = st.session_state[f"user_question_input_{st.session_state.text_input_key_counter}"].strip()
    if current_text:
        # Garante que não vamos reprocessar áudio se o texto foi digitado
        st.session_state.audio_to_process = None 
        st.session_state.processing_audio_step = ""
        st.session_state.last_processed_audio_hash = None # Limpa o hash do áudio processado
        
        process_query_and_get_response(current_text)
        st.session_state.user_question_text = "" # Limpa o input após processar o texto digitado
    else:
        st.toast("⚠️ Por favor, digite uma pergunta válida.")
        st.session_state.user_question_text = ""


def handle_Youtubeing():
    st.header("🔍 Perguntar sobre conteúdo")

    col1, col2 = st.columns([8, 1])

    with col1:
        st.text_input(
            "Digite sua pergunta (pressione Enter para perguntar):",
            value=st.session_state.user_question_text,
            key=f"user_question_input_{st.session_state.text_input_key_counter}",
            on_change=on_text_input_submit
        )

    with col2:
        # mic_recorder sem callback direto, apenas retorna audio_data
        current_mic_audio_data = mic_recorder(
            start_prompt="🎤",
            stop_prompt="✅",
            key="mic_recorder"
        )
        
    # Calcular um hash simples do áudio para verificar se é novo
    current_audio_hash = None
    if current_mic_audio_data and current_mic_audio_data.get('bytes'):
        current_audio_hash = hash(current_mic_audio_data['bytes']) # Cria um hash dos bytes do áudio

    # Lógica de processamento de áudio:
    # Este bloco é executado SE:
    # 1. Há audio_data (algo foi gravado).
    # 2. NÃO há áudio já agendado para processamento (audio_to_process é None).
    # 3. O áudio atual é DIFERENTE do último áudio que já foi processado (evita reprocessar o mesmo áudio).
    if current_mic_audio_data and current_mic_audio_data.get('bytes') and \
       not st.session_state.audio_to_process and \
       current_audio_hash != st.session_state.last_processed_audio_hash:
        
        st.session_state.audio_to_process = current_mic_audio_data['bytes']
        st.session_state.processing_audio_step = "transcribing" # Sinaliza o início da transcrição
        st.session_state.last_processed_audio_hash = current_audio_hash # Armazena o hash do áudio que será processado
        st.session_state.text_input_key_counter += 1 # Para resetar/atualizar o input visualmente
        st.rerun() # Força o rerun para iniciar o processamento do áudio

    # Bloco para processar o áudio (transcrição e consulta à IA)
    # Este bloco só roda SE houver áudio para processar E a etapa estiver definida
    if st.session_state.audio_to_process and st.session_state.processing_audio_step:
        # Step 1: Transcribing
        if st.session_state.processing_audio_step == "transcribing":
            st.toast("🎙️ Transcrevendo áudio...")
            st.audio(st.session_state.audio_to_process, format="audio/wav")

            spinner_placeholder_transcribe = st.empty()
            with spinner_placeholder_transcribe.container():
                st.info("Transcrevendo áudio...") # Spinner fixo durante a transcrição
            
            try:
                transcript = st.session_state.transcription.transcribe(io.BytesIO(st.session_state.audio_to_process))
                st.session_state.user_question_text = transcript # Atualiza o input de texto
                st.toast("✅ Transcrição concluída!")

                # Mover para a próxima etapa: consulta à IA
                st.session_state.processing_audio_step = "querying_ai"
                st.rerun() # Força rerun para exibir a transcrição e iniciar consulta à IA
            except Exception as e:
                st.error(f"❌ Erro na transcrição: {e}")
                st.session_state.response = f"Não foi possível transcrever: {e}"
                st.session_state.user_question_text = ""
                st.session_state.audio_to_process = None # Limpa o áudio
                st.session_state.processing_audio_step = "" # Reseta a etapa
                st.session_state.last_processed_audio_hash = None # Limpa o hash em caso de erro
            finally:
                spinner_placeholder_transcribe.empty() # Garante que o spinner de transcrição seja limpo

        # Step 2: Querying AI after transcription
        elif st.session_state.processing_audio_step == "querying_ai":
            query_text_from_audio = st.session_state.user_question_text
            
            if query_text_from_audio: # Garante que a transcrição não seja vazia
                process_query_and_get_response(query_text_from_audio)
                st.session_state.user_question_text = "" # Limpa o input após a resposta da IA

            # Reseta os estados do áudio para a próxima interação
            st.session_state.audio_to_process = None
            st.session_state.processing_audio_step = ""
            st.session_state.last_processed_audio_hash = None # Limpa o hash após o processamento completo

            # Um último rerun pode ser necessário para garantir que o input seja limpo e a resposta apareça
            # Se a resposta não estiver aparecendo, descomente a linha abaixo.
            # st.rerun() 

    # Mostrar resposta
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
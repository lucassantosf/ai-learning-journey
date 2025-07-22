import streamlit as st
import io
from streamlit_mic_recorder import mic_recorder

from src.pipelines.pdf_pipeline import process_pdf_file
from src.pipelines.rag_pipeline import RAG
from src.pipelines.summarizer import Summarizer
from src.core.chunking import TextChunker
from src.services.transcription_service import TranscriptionService

def init_session_state():
    """Initialize session state variables."""
    st.session_state.setdefault("rag_system", RAG())
    st.session_state.setdefault("summarizer", Summarizer())
    st.session_state.setdefault("transcription", TranscriptionService())

    st.session_state.setdefault("input_key_counter", 0)
    st.session_state.setdefault("mic_input_key", 0)
    st.session_state.setdefault("response", "")

    st.session_state.setdefault("audio_to_process", None)
    st.session_state.setdefault("processing_audio_step", "")
    st.session_state.setdefault("last_processed_audio_hash", None)

def handle_pdf_upload():
    st.header("PDF Upload")
    pdf_file = st.file_uploader("Upload a PDF with study content", type=["pdf"])

    if pdf_file:
        with st.spinner("Processing PDF..."):
            try:
                chunks = process_pdf_file(pdf_file)
                st.session_state.rag_system.add_documents(chunks)
                full_text = " ".join(chunk["text"] for chunk in chunks)
                st.session_state.full_text = full_text
                st.success(f"PDF '{pdf_file.name}' loaded with {len(chunks)} chunks.")
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                return

        with st.spinner("Generating summary and questions..."):
            summarizer = st.session_state.summarizer
            try:
                summary = summarizer.generate_summary(full_text)
                st.subheader("Summary:")
                st.write(summary)

                num_questions = st.session_state.num_questions
                questions = summarizer.generate_questions(full_text, num_questions)
                st.subheader("Generated Questions:")
                for q in questions:
                    st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")
            except Exception as e:
                st.error(f"Error generating summary and questions: {str(e)}")

def handle_manual_text():
    st.header("Enter Text Manually")
    content = st.text_area("Paste or type the content", height=300)

    if st.button("Process Text"):
        if not content.strip():
            st.error("Please enter some text.")
            return

        with st.spinner("Processing text..."):
            rag_system = st.session_state.rag_system
            summarizer = st.session_state.summarizer

            chunks = TextChunker().create_chunks(content, source="manual_input")
            rag_system.add_documents(chunks)
            st.session_state.full_text = content

            summary = summarizer.generate_summary(content)
            st.subheader("Summary:")
            st.write(summary)

            num_questions = st.session_state.num_questions
            questions = summarizer.generate_questions(content, num_questions)
            st.subheader("Generated Questions:")
            for q in questions:
                st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

def process_query_and_get_response(query_text: str):
    if not query_text.strip():
        st.toast("Please enter or record a valid question.")
        st.session_state.response = ""
        return

    st.session_state.response = ""

    spinner_placeholder_ai = st.empty()
    with spinner_placeholder_ai.container():
        st.info("Consulting AI...")

    try:
        rag = st.session_state.rag_system
        response = rag.query_and_respond(query_text, n_results=1)
        st.session_state.response = response
        st.toast("Response generated!")
    except Exception as e:
        st.error(f"Error fetching response: {e}")
        st.session_state.response = f"Could not obtain a response: {e}"
    finally:
        spinner_placeholder_ai.empty()

def on_text_input_submit():
    key = f"user_question_input_{st.session_state.input_key_counter}"
    query = st.session_state.get(key, "").strip()

    if query:
        st.session_state.audio_to_process = None
        st.session_state.processing_audio_step = ""
        st.session_state.last_processed_audio_hash = None
        st.session_state.response = ""
        process_query_and_get_response(query)
        st.session_state.input_key_counter += 1
    else:
        st.toast("Please enter a valid question.")

def handle_questioning():
    st.header("Ask About Content")

    st.text_input(
        "Enter your question or record your voice (press Enter to ask):",
        key=f"user_question_input_{st.session_state.input_key_counter}",
        on_change=on_text_input_submit
    )

    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="✅", key=f"mic_recorder_{st.session_state.mic_input_key}")

    if (
        st.session_state.audio_to_process is None
        and audio_data and audio_data.get('bytes')
        and not st.session_state.get("processing_audio_step")
    ):
        current_hash = hash(audio_data["bytes"])
        if current_hash != st.session_state.last_processed_audio_hash:
            st.session_state.audio_to_process = audio_data['bytes']
            st.session_state.processing_audio_step = "transcribing"
            st.session_state.last_processed_audio_hash = current_hash
            st.rerun()

    if st.session_state.processing_audio_step == "transcribing":
        st.toast("Transcribing audio...")
        st.audio(st.session_state.audio_to_process, format="audio/wav")
        with st.spinner("Transcribing..."):
            try:
                transcript = st.session_state.transcription.transcribe(io.BytesIO(st.session_state.audio_to_process))
                st.toast("Transcription completed!")
                process_query_and_get_response(transcript)

                # Clearing state + resetting audio key
                st.session_state.audio_to_process = None
                st.session_state.processing_audio_step = ""
                st.session_state.last_processed_audio_hash = None
                st.session_state.input_key_counter += 1
                st.session_state.mic_input_key += 1  # RESET recorder!

                st.rerun()

            except Exception as e:
                st.error(f"Error transcribing: {e}")
                st.session_state.processing_audio_step = ""
                st.session_state.audio_to_process = None
                st.session_state.mic_input_key += 1  # prevent loop

    if st.session_state.response:
        st.subheader("Response Found:")
        st.write(st.session_state.response)

def main():
    st.set_page_config(page_title="Summarizer", layout="wide")

    init_session_state()

    st.title("📚 Summarizer: Learn with AI")
    st.write("Generate summaries, questions, and consult content with AI (text, PDF, or voice).")

    st.sidebar.header("🔷 Main Menu")
    menu = st.sidebar.radio(
        "Choose usage mode:",
        ["PDF Upload", "Enter Text Manually", "Ask About Content"]
    )

    st.sidebar.header("🔧 Settings")
    st.session_state.num_questions = st.sidebar.slider(
        "Number of questions/flashcards", min_value=3, max_value=7, value=5
    )

    if menu == "PDF Upload":
        handle_pdf_upload()
    elif menu == "Enter Text Manually":
        handle_manual_text()
    elif menu == "Ask About Content":
        handle_questioning()

    st.markdown("---")
    st.caption("Developed by XXX. Powered by LLMs & Streamlit")

if __name__ == "__main__":
    main()

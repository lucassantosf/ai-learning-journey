import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import os
import io
from dotenv import load_dotenv
from src.core.llm import LLMClient

load_dotenv()

# Configure your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"

st.set_page_config(page_title="Audio Recorder and Transcriber", layout="centered")

st.title("🎤 Audio Recorder and Whisper Transcriber")
st.markdown("---")

st.write("Click on the microphone to start recording. Click again to stop.")

# Using mic_recorder with icons and visual feedback
# The component can now display an icon and change the text
audio_data = mic_recorder(
    start_prompt="🔴 Record", # Recording icon and text
    stop_prompt="✅ Stop Recording", # Success icon and text
    key="mic_recorder",
    # Optional: for a simple audio visualizer during recording
    # show_visualizer=True # Depends on version, may not be available or not be what you expect
)

if audio_data:
    st.success("Audio recorded successfully!")
    st.audio(audio_data['bytes'], format="audio/wav")

    st.write("Transcribing audio...")
    try:
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "recorded_audio.wav"

        transcript = LLMClient(use_openai=True).transcript(audio_file)
        
        st.success("Transcription Completed!")
        st.markdown(f"**Transcription:**\n```\n{transcript}\n```")
    except openai.APIError as e:
        st.error(f"Error during transcription: {e}")
        st.info("Please ensure your OpenAI API key is valid and you have sufficient credits.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.write("This prototype uses `streamlit-mic-recorder` to capture audio and OpenAI's Whisper for transcription.")

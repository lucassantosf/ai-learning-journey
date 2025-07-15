import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import os
import io
from dotenv import load_dotenv

load_dotenv()

# Configura sua chave da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY") or "SUA_CHAVE_API_OPENAI"

st.set_page_config(page_title="Gravador e Transcritor", layout="centered")

st.title("🎤 Gravador de Áudio e Transcritor Whisper")
st.markdown("---")

st.write("Clique no microfone para iniciar a gravação. Clique novamente para parar.")

# Usando o mic_recorder com ícones e feedback visual
# O componente agora pode exibir um ícone e mudar o texto
audio_data = mic_recorder(
    start_prompt="🔴 Gravar", # Ícone de gravação e texto
    stop_prompt="✅ Parar Gravação", # Ícone de sucesso e texto
    key="mic_recorder",
    # Opcional: para um visualizador simples de áudio durante a gravação
    # show_visualizer=True # Depende da versão, pode não estar disponível ou não ser o que você espera
)

if audio_data:
    st.success("Áudio gravado com sucesso!")
    st.audio(audio_data['bytes'], format="audio/wav")

    st.write("Transcrevendo áudio...")
    try:
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "recorded_audio.wav"

        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        st.success("Transcrição Concluída!")
        st.markdown(f"**Transcrição:**\n```\n{transcript.text}\n```")
    except openai.APIError as e:
        st.error(f"Erro durante a transcrição: {e}")
        st.info("Por favor, garanta que sua chave da API OpenAI é válida e você tem créditos suficientes.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")

st.markdown("---")
st.write("Este protótipo usa `streamlit-mic-recorder` para capturar áudio e o Whisper da OpenAI para transcrição.")
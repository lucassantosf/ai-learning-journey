import io
from openai import OpenAI
from src.config import OPENAI_API_KEY

class TranscriptionService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        audio_file = ("recorded_audio.wav", audio_bytes)

        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text

import io
from openai import OpenAI
from src.config import OPENAI_API_KEY

class TranscriptionService:
    def __init__(self):
        """
        Initialize the transcription service with OpenAI's API key.
        Uses the Whisper model for audio transcription.
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text using OpenAI's Whisper model.

        Args:
            audio_bytes (bytes): Raw audio data to be transcribed.

        Returns:
            str: Transcribed text from the audio.
        """
        audio_file = ("recorded_audio.wav", audio_bytes)

        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text

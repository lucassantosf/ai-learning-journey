import os
import requests
from openai import OpenAI
from src.config import USE_OPENAI, OPENAI_API_KEY

class LLMClient:
    def __init__(self, use_openai=USE_OPENAI):
        self.use_openai = use_openai
        self.model = "gpt-4o" if self.use_openai else "llama3.2:1b"

        if self.use_openai:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY não definido.")
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            self.client = OpenAI()
        else:
            self.ollama_url = "http://localhost:11434/api/chat"

    def chat(self, messages, max_tokens=500):
        if self.use_openai:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens
            )
            return res.choices[0].message.content.strip()
        else:
            res = requests.post(
                self.ollama_url,
                json={"model": self.model, "messages": messages, "stream": False}
            )
            data = res.json()
            return data.get("message", {}).get("content", "").strip()

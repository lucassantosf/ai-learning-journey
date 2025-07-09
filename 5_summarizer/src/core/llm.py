import os
import requests
from openai import OpenAI

class LLMClient:
    def __init__(self, use_openai=False, model=None):
        self.use_openai = use_openai
        self.model = model or ("gpt-4o" if use_openai else "llama3.2:1b")

        if use_openai:
            from dotenv import load_dotenv

            # Suppress tokenizer warnings
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment.")

            os.environ["OPENAI_API_KEY"] = api_key  
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
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"].strip()
            else:
                raise ValueError(f"Ollama response missing expected fields: {data}")

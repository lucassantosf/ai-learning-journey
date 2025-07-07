import os
import requests
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient

load_dotenv()

class Summarizer:
    def __init__(self, use_openai=False):
        self.use_openai = use_openai
        self.model = "gpt-4o" if use_openai else "llama3.2:1b"
        
        if use_openai:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment.")
            self.client = OpenAIClient(api_key=api_key)
        else:
            self.ollama_url = "http://localhost:11434/api/chat"

    def _chat(self, messages, max_tokens=500):
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

    def generate_summary(self, text, max_words=20):
        prompt = f"Summarize this text in under {max_words} words:\n\n{text}"
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ]
        return self._chat(messages, max_tokens=max_words)

    def generate_questions(self, text, num_questions=5):
        prompt = f"Generate {num_questions} study questions with answers based on this text:\n\n{text}"
        messages = [
            {"role": "system", "content": "You create exam-style study questions."},
            {"role": "user", "content": prompt}
        ]
        raw = self._chat(messages)

        questions = []
        current_q, current_a = "", []

        for line in raw.splitlines():
            if any(line.strip().lower().startswith(p) for p in ["q", "question", "1.", "2.", "3.", "4.", "5."]):
                if current_q:
                    questions.append({"question": current_q, "answer": " ".join(current_a).strip()})
                current_q = line.split(":", 1)[-1].strip()
                current_a = []
            elif current_q:
                current_a.append(line.strip())

        if current_q:
            questions.append({"question": current_q, "answer": " ".join(current_a).strip()})

        return questions[:num_questions]

if __name__ == "__main__":
    summarizer = Summarizer(use_openai=False)  # True para usar OpenAI

    texto = """Artificial Intelligence (AI) is an area of computer science that mimics human intelligence. It involves developing algorithms and machines that can think, learn, and act like humans. In essence, AI simulates the way we think, making decisions, and solve problems. The goal of AI research is to create intelligent systems that can interact with humans in a meaningful way.
            Currently, AI is being developed in various fields such as machine learning, natural language processing, and computer vision. These technologies enable machines to recognize patterns, make predictions, and generate responses similar to human behavior. Some examples of AI applications include virtual assistants like Siri, Alexa, and Google Assistant, self-driving cars, medical diagnosis systems, and recommendation engines.
            The development of AI has far-reaching implications for various industries, including healthcare, finance, education, and transportation. By creating intelligent machines, humans can automate routine tasks, reduce errors, and improve decision-making processes. However, the field of AI is also facing challenges such as ensuring fairness, transparency, and accountability in machine learning algorithms.
            Overall, artificial intelligence is a rapidly evolving field that holds great promise for transforming industries and improving human lives. As research continues to advance, we can expect to see more sophisticated AI systems that can learn, adapt, and interact with humans in a way that simulates the complexity of human intelligence."""

    print("Resumo:")
    print(summarizer.generate_summary(texto))

    print("\n❓ Perguntas:")
    for q in summarizer.generate_questions(texto, num_questions=3):
        print(f"- Q: {q['question']}\n  A: {q['answer']}\n")

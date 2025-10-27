from typing import List, Dict, Any
import pytest
from src.agents.rag_agent import RAGAgent

# Dummy Retriever que retorna trechos fixos
class DummyRetriever:
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return [
            {"text": "Documento sobre gatos.", "score": 0.95, "metadata": {"id": 1}},
            {"text": "Informações sobre cachorros.", "score": 0.90, "metadata": {"id": 2}},
        ][:top_k]

# Dummy LLM que simula resposta
class DummyLLMClient:
    class Chat:
        class completions:
            @staticmethod  # ⚠️ define como método estático
            def create(model, messages, temperature):
                # Retorna uma estrutura compatível com OpenAI ChatCompletion
                return type(
                    "Response",
                    (),
                    {"choices": [type("Choice", (), {"message": type("Message", (), {"content": "Resposta simulada do LLM"})()})()]}
                )()
    def __init__(self):
        self.chat = self.Chat()

def test_rag_agent_basic():
    retriever = DummyRetriever()
    dummy_llm = DummyLLMClient()

    agent = RAGAgent(retriever=retriever, client=dummy_llm)
    question = "Qual é a informação sobre animais?"

    answer = agent.ask(question, top_k=2)

    assert isinstance(answer, str)
    assert "simulada" in answer  # verifica se o dummy LLM foi chamado

def test_rag_agent_no_results():
    class EmptyRetriever:
        def search(self, query: str, top_k: int = 5):
            return []

    agent = RAGAgent(retriever=EmptyRetriever(), client=DummyLLMClient())
    answer = agent.ask("Pergunta sem documentos")
    assert answer == "No relevant documents found."

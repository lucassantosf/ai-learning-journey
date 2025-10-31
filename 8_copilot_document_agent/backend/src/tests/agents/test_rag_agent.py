import pytest
from typing import List, Dict, Any
from src.agents.rag_agent import RAGAgent


# ----------------------------
# Dummies (mantidos e expandidos)
# ----------------------------
class DummyRetriever:
    def __init__(self, results=None):
        self.results = results or [
            {"text": "Documento sobre gatos.", "score": 0.95, "metadata": {"id": 1}},
            {"text": "Informações sobre cachorros.", "score": 0.90, "metadata": {"id": 2}},
        ]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.results[:top_k]


class DummyLLMClient:
    class Chat:
        class Completions:
            @staticmethod
            def create(model, messages, temperature):
                # Simula comportamento do OpenAI client
                content = f"Resposta simulada do modelo {model} com prompt: {messages[0]['content'][:30]}..."
                return type(
                    "Response",
                    (),
                    {"choices": [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]}
                )()

        completions = Completions()

    def __init__(self):
        self.chat = self.Chat()


# ----------------------------
# TESTES
# ----------------------------

def test_rag_agent_basic():
    retriever = DummyRetriever()
    dummy_llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=dummy_llm)

    question = "Qual é a informação sobre animais?"
    answer = agent.ask(question, top_k=2)

    assert isinstance(answer, str)
    assert "Resposta simulada" in answer
    assert "gpt-4o-mini" in answer


def test_rag_agent_no_results():
    class EmptyRetriever:
        def search(self, query: str, top_k: int = 5):
            return []

    agent = RAGAgent(retriever=EmptyRetriever(), client=DummyLLMClient())
    answer = agent.ask("Pergunta sem documentos")
    assert answer == "No relevant documents found."


# 1️⃣ Resposta para documentos sem contexto relevante
def test_rag_agent_irrelevant_context():
    retriever = DummyRetriever(results=[{"text": "", "score": 0.0, "metadata": {}}])
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    result = agent.ask("O que diz o documento?")
    assert isinstance(result, str)
    assert "Resposta simulada" in result


# 2️⃣ Comportamento com diferentes tamanhos de top_k
@pytest.mark.parametrize("top_k", [1, 2, 3, 5])
def test_rag_agent_respects_top_k(top_k):
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    agent.ask("Pergunta genérica", top_k=top_k)
    results = retriever.search("Pergunta genérica", top_k=top_k)

    assert len(results) <= top_k


# 3️⃣ Verificação do prompt gerado
def test_rag_agent_prompt_generation(monkeypatch):
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    captured_prompt = {}

    def fake_create(model, messages, temperature):
        captured_prompt["prompt"] = messages[0]["content"]
        return DummyLLMClient.Chat.Completions.create(model, messages, temperature)

    # substitui método original por um mock
    monkeypatch.setattr(llm.chat.completions, "create", fake_create)

    question = "O que contém o documento?"
    agent.ask(question)

    prompt = captured_prompt["prompt"]
    assert "Use the following context" in prompt
    assert "Question:" in prompt
    assert question in prompt
    assert "Documento sobre gatos" in prompt


# 4️⃣ Fallback para respostas quando não há contexto
def test_rag_agent_fallback_message():
    class EmptyRetriever:
        def search(self, query: str, top_k: int = 5):
            return []

    llm = DummyLLMClient()
    agent = RAGAgent(retriever=EmptyRetriever(), client=llm)

    result = agent.ask("Sem contexto relevante")
    assert result == "No relevant documents found."


# 5️⃣ Verificação de robustez com erro do LLM
def test_rag_agent_handles_llm_error(monkeypatch):
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    def broken_create(*args, **kwargs):
        raise RuntimeError("Falha simulada no LLM")

    monkeypatch.setattr(llm.chat.completions, "create", broken_create)

    with pytest.raises(RuntimeError):
        agent.ask("Pergunta que quebra o LLM")
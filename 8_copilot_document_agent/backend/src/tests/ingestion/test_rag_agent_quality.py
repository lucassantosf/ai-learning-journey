import pytest
import difflib
import math
from src.agents.rag_agent import RAGAgent


# =========================================================
# Dummies Reutilizados
# =========================================================
class DummyRetriever:
    def __init__(self, results=None):
        self.results = results or [
            {"text": "O Python é uma linguagem de programação amplamente usada em IA.", "score": 0.98},
            {"text": "O Java é uma linguagem robusta para aplicações corporativas.", "score": 0.90},
        ]

    def search(self, query: str, top_k: int = 5):
        return self.results[:top_k]


class DummyLLMClient:
    class Chat:
        class Completions:
            @staticmethod
            def create(model, messages, temperature):
                prompt = messages[0]["content"]
                # Simula uma resposta do LLM baseada no conteúdo do prompt
                if "Python" in prompt:
                    content = "O Python é amplamente utilizado em inteligência artificial, pois possui diversas bibliotecas para aprendizado de máquina."
                elif "Java" in prompt:
                    content = "O Java é mais usado para aplicações empresariais e sistemas robustos."
                else:
                    content = "Não encontrei informações relevantes nos documentos."
                return type(
                    "Response",
                    (),
                    {"choices": [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]}
                )()

        completions = Completions()

    def __init__(self):
        self.chat = self.Chat()


# =========================================================
# Testes Qualitativos (como antes)
# =========================================================
def test_rag_agent_relevance():
    """Verifica se a resposta gerada é relevante em relação ao contexto."""
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    question = "Como o Python é usado em IA?"
    answer = agent.ask(question)

    assert "Python" in answer or "inteligência artificial" in answer
    assert "Java" not in answer, "A resposta deve ser relevante ao contexto do Python."


def test_rag_agent_source_citation(monkeypatch):
    """Verifica se o prompt enviado contém o conteúdo dos documentos fonte."""
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    captured_prompt = {}

    def fake_create(model, messages, temperature):
        captured_prompt["prompt"] = messages[0]["content"]
        return DummyLLMClient.Chat.Completions.create(model, messages, temperature)

    monkeypatch.setattr(llm.chat.completions, "create", fake_create)

    _ = agent.ask("Quais linguagens são mencionadas?")

    prompt = captured_prompt["prompt"]
    assert "Python" in prompt
    assert "Java" in prompt
    assert "Question:" in prompt


def test_rag_agent_technical_question():
    """Testa perguntas técnicas específicas."""
    retriever = DummyRetriever(results=[
        {"text": "O Python é uma linguagem interpretada e multiparadigma.", "score": 0.97}
    ])
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    question = "O Python é compilado ou interpretado?"
    answer = agent.ask(question)

    assert isinstance(answer, str)
    assert "interpretada" in answer or "Python" in answer


# =========================================================
# Testes Quantitativos de Qualidade
# =========================================================

def similarity_ratio(a: str, b: str) -> float:
    """Retorna a similaridade textual entre duas strings (0 a 1)."""
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def test_rag_agent_semantic_similarity():
    """
    Mede a similaridade entre a resposta gerada e a resposta esperada.
    """
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    question = "Como o Python é usado em IA?"
    expected_answer = "O Python é amplamente utilizado em inteligência artificial, com várias bibliotecas como TensorFlow e PyTorch."

    answer = agent.ask(question)
    score = similarity_ratio(answer, expected_answer)

    # Espera-se uma similaridade alta (> 0.6 é aceitável)
    assert score > 0.6, f"Similaridade baixa ({score:.2f}) entre resposta gerada e esperada."


def test_rag_agent_context_relevance_score():
    """
    Mede o quanto a resposta é coerente com o contexto retornado pelo retriever.
    """
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    question = "Fale sobre linguagens de programação para IA."
    answer = agent.ask(question)

    # Considera que o contexto relevante contém "Python"
    relevance_score = 1.0 if "Python" in answer else 0.0
    assert relevance_score > 0, "A resposta não faz referência ao contexto relevante (Python)."


def test_rag_agent_noisy_input_handling():
    """
    Testa se o modelo ainda responde de forma coerente a perguntas com ruído.
    """
    retriever = DummyRetriever()
    llm = DummyLLMClient()
    agent = RAGAgent(retriever=retriever, client=llm)

    question = "##!! Como... o PYTHON é usado     em     IA ???"
    answer = agent.ask(question)

    assert isinstance(answer, str)
    assert "Python" in answer
    assert "inteligência artificial" in answer
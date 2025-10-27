from typing import List
from src.retrieval.retriever import Retriever
from openai import OpenAI

class RAGAgent:
    """
    Agente RAG: consulta documentos via Retriever e gera resposta usando LLM.
    """

    def __init__(self, retriever: Retriever, model_name: str = "gpt-4o-mini", client: OpenAI = None):
        self.retriever = retriever
        self.model_name = model_name
        self.client = client or OpenAI()

    def _build_prompt(self, question: str, contexts: List[str]) -> str:
        """
        Constrói o prompt combinando contexto dos documentos e pergunta.
        """
        context_text = "\n\n".join(contexts)
        prompt = (
            f"Use the following context from documents to answer the question:\n\n"
            f"{context_text}\n\n"
            f"Question: {question}\n"
            f"Answer:"
        )
        return prompt

    def ask(self, question: str, top_k: int = 5) -> str:
        """
        Busca trechos relevantes e gera a resposta do LLM.
        """
        # 1️⃣ Recupera trechos
        results = self.retriever.search(question, top_k=top_k)
        contexts = [r["text"] for r in results]

        if not contexts:
            return "No relevant documents found."

        # 2️⃣ Monta prompt
        prompt = self._build_prompt(question, contexts)

        # 3️⃣ Chama LLM
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        # 4️⃣ Retorna texto da resposta
        return response.choices[0].message.content

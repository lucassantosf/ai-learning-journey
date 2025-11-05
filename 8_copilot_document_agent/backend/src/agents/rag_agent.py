from typing import List, Dict, Any
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

    def run_with_trace(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Executa o RAG e retorna o raciocínio e ferramentas usadas.
        """
        reasoning_steps = []
        tools_used = []

        reasoning_steps.append("🔎 Buscando contextos relevantes com FAISS retriever...")
        tools_used.append("faiss_retriever")

        results = self.retriever.search(question, top_k=top_k)
        contexts = [r["text"] for r in results]

        if not contexts:
            return {
                "reasoning": "\n".join(reasoning_steps) + "\n⚠️ Nenhum documento relevante encontrado.",
                "tools_used": tools_used,
                "final_answer": "No relevant documents found."
            }

        reasoning_steps.append(f"🧩 {len(contexts)} trechos relevantes encontrados. Gerando resposta com LLM...")
        tools_used.append("llm")

        prompt = self._build_prompt(question, contexts)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        answer = response.choices[0].message.content.strip()
        reasoning_steps.append("✅ Resposta gerada com sucesso.")

        return {
            "reasoning": "\n".join(reasoning_steps),
            "tools_used": tools_used,
            "final_answer": answer
        }
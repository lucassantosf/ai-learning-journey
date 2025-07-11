from src.core.vector_store import VectorStore
from src.core.llm import LLMClient

class RAG:
    """Sistema RAG simples com LLM + vetores"""

    def __init__(self, use_openai=False):
        self.vector_store = VectorStore()
        self.llm = LLMClient(use_openai=use_openai)

    def add_documents(self, chunks):
        self.vector_store.add_documents(chunks)

    def query_and_respond(self, query, n_results=3):
        result = self.vector_store.query(query, n_results=n_results)
        context = "\n".join(doc for doc in result["documents"][0])
        prompt = f"""Based on the context below, answer the question. 
                    If no answer is found, reply with 'I don't know'.

                    Context:
                    {context}

                    Question:
                    {query}

                    Answer:"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        return self.llm.chat(messages)

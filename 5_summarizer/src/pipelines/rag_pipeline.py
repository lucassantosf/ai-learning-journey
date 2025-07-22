from src.core.vector_store import VectorStore
from src.core.llm import LLMClient

class RAG:
    """Simple RAG system with LLM + vectors"""

    def __init__(self, use_openai=True):
        """
        Initialize the Retrieval-Augmented Generation (RAG) system.

        Args:
            use_openai (bool, optional): Whether to use OpenAI's LLM. Defaults to True.
        """
        self.vector_store = VectorStore()
        self.llm = LLMClient(use_openai=use_openai)

    def add_documents(self, chunks):
        """
        Add documents to the vector store.

        Args:
            chunks (list): List of document chunks to be added.
        """
        self.vector_store.add_documents(chunks)

    def query_and_respond(self, query, n_results=3):
        """
        Retrieve relevant context and generate a response to the query.

        Args:
            query (str): The user's query.
            n_results (int, optional): Number of context documents to retrieve. Defaults to 3.

        Returns:
            str: Generated response based on the retrieved context.
        """
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

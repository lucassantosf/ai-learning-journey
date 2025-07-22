from src.config import CHROMA_PERSIST_PATH, VECTOR_STORE_COLLECTION
import chromadb
from chromadb.utils import embedding_functions
import os

class VectorStore:
    def __init__(self):
        """
        Initialize a persistent vector store using ChromaDB.

        Creates a directory for persistent storage and sets up a collection
        with a default embedding function. Handles potential errors by 
        attempting to reset and recreate the collection if needed.
        """
        os.makedirs(CHROMA_PERSIST_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        try:
            # Force collection creation, create if it doesn't exist
            self.collection = self.client.get_or_create_collection(
                name=VECTOR_STORE_COLLECTION, embedding_function=self.embedding_fn
            )
        except ValueError as e:
            print(f"[VectorStore] Error accessing collection, attempting to reset: {e}")
            self._reset_and_recreate()

    def _reset_and_recreate(self):
        """
        Reset the entire client and recreate the collection.

        Used when the database or tenant has been deleted or corrupted.
        Clears all existing collections and creates a new one.
        """
        self.client.reset()  # clear all collections
        self.collection = self.client.get_or_create_collection(
            name=VECTOR_STORE_COLLECTION, embedding_function=self.embedding_fn
        )
        print("[VectorStore] Collection recreated after reset.")

    def add_documents(self, chunks):
        """
        Add documents to the vector store collection.

        Args:
            chunks (list): A list of document chunks to be added.
                Each chunk should be a dictionary with 'id', 'text', and optional 'metadata'.
        """
        for chunk in chunks:
            if not chunk.get("metadata"):
                chunk["metadata"] = {"info": "default"}
        self.collection.add(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks]
        )

    def query(self, query, n_results=3):
        """
        Perform a similarity search in the vector store.

        Args:
            query (str): The query text to search for similar documents.
            n_results (int, optional): Number of similar documents to return. Defaults to 3.

        Returns:
            dict: Query results containing similar documents and their metadata.
        """
        return self.collection.query(query_texts=[query], n_results=n_results)

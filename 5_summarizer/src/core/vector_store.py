from src.config import CHROMA_PERSIST_PATH, VECTOR_STORE_COLLECTION
import chromadb
from chromadb.utils import embedding_functions
import os

class VectorStore:
    def __init__(self):
        os.makedirs(CHROMA_PERSIST_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=VECTOR_STORE_COLLECTION, embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks):
        for chunk in chunks:
            if not chunk.get("metadata"):
                chunk["metadata"] = {"info": "default"}

        self.collection.add(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks]
        )

    def query(self, query, n_results=3):
        return self.collection.query(query_texts=[query], n_results=n_results)

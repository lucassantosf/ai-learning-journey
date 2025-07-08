import chromadb
from chromadb.utils import embedding_functions
import os

class VectorStore:
    def __init__(self, collection_name="default", persist_path="./db/chroma_persist"):
        os.makedirs(persist_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_fn
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

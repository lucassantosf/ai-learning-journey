from src.config import CHROMA_PERSIST_PATH, VECTOR_STORE_COLLECTION
import chromadb
from chromadb.utils import embedding_functions
import os

class VectorStore:
    def __init__(self):
        os.makedirs(CHROMA_PERSIST_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        try:
            # Força criação da collection, cria caso não exista
            self.collection = self.client.get_or_create_collection(
                name=VECTOR_STORE_COLLECTION, embedding_function=self.embedding_fn
            )
        except ValueError as e:
            print(f"[VectorStore] Erro ao acessar collection, tentando resetar: {e}")
            self._reset_and_recreate()

    def _reset_and_recreate(self):
        # Caso o banco/tenant tenha sido apagado ou corrompido, recria tudo
        self.client.reset()  # limpa todas as collections
        self.collection = self.client.get_or_create_collection(
            name=VECTOR_STORE_COLLECTION, embedding_function=self.embedding_fn
        )
        print("[VectorStore] Collection criada novamente após reset.")

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

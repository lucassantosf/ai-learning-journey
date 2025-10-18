from src.core.logger import log_info

class FaissVectorStore:
    def __init__(self, path: str):
        self.path = path
        log_info(f"Inicializando FAISS em: {self.path}")

    def add_embeddings(self, embeddings):
        log_info(f"Adicionando {len(embeddings)} embeddings ao FAISS...")
        # TODO: Implementar FAISS real (index, add, save)
        pass
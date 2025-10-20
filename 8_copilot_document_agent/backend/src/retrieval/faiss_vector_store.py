from src.core.logger import log_info

class FaissVectorStore:
    def __init__(self, path: str = None):
        # Use um caminho padrão se nenhum for fornecido
        self.path = path or os.path.join(os.getcwd(), 'faiss_index')
        log_info(f"Inicializando FAISS em: {self.path}")

    def add_embeddings(self, embeddings):
        log_info(f"Adicionando {len(embeddings)} embeddings ao FAISS...")
        # TODO: Implementar FAISS real (index, add, save)
        pass
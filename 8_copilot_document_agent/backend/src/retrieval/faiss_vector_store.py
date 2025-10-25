import faiss
import numpy as np
import os
from typing import List, Optional
from src.core.logger import log_info

class FaissVectorStore:
    """FAISS index simples com armazenamento de metadados e persistência."""

    def __init__(self, embedding_dim: int = 1536, path: Optional[str] = None):
        """
        :param embedding_dim: dimensão esperada dos embeddings
        :param path: caminho do arquivo para persistir o índice (faiss binary)
        """
        self.embedding_dim = embedding_dim
        self.path = path if path else None
        # cria índice em memória
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata: List[dict] = []

        # se existe arquivo salvo, tenta carregar
        if self.path and os.path.exists(self.path):
            try:
                self.load()
            except Exception as e:
                log_info(f"⚠️ Falha ao carregar índice FAISS de {self.path}: {e}")

    def add_embeddings(self, vectors: List[List[float]], metadatas: Optional[List[dict]] = None):
        if not vectors:
            return

        # converte para array float32
        array = np.array(vectors, dtype="float32")

        # validações
        if len(array.shape) != 2:
            log_info(f"❌ Vetores malformados: shape={array.shape}. Verifique dimensões inconsistentes.")
            raise ValueError(f"Vetores malformados: shape={array.shape}")

        if array.shape[1] != self.embedding_dim:
            log_info(f"❌ Dimensão incorreta dos embeddings! Esperado {self.embedding_dim}, recebido {array.shape[1]}")
            raise ValueError(f"Dimensão incorreta dos embeddings! Esperado {self.embedding_dim}, recebido {array.shape[1]}")

        # adiciona ao índice
        try:
            self.index.add(array)
        except Exception as e:
            log_info(f"❌ Erro ao adicionar vetores ao FAISS: {e}")
            raise

        # armazena metadados (se fornecido)
        if metadatas:
            if len(metadatas) != len(vectors):
                log_info("⚠️ Número de metadatas diferente do número de vetores. Ajustando pelo mínimo.")
            self.metadata.extend(metadatas)

        log_info(f"✅ Adicionados {array.shape[0]} vetores ao FAISS.")

    def search(self, query_vector: List[float], k: int = 5):
        """
        Busca no índice.
        Retorna (distances, indices) como numpy arrays, para compatibilidade com os testes.
        """
        q = np.array([query_vector], dtype="float32")
        if q.shape[1] != self.index.d:
            raise ValueError(f"Dimensão do vetor de consulta incorreta. Esperado {self.index.d}, recebido {q.shape[1]}")

        D, I = self.index.search(q, k)
        return D, I

    def get_stats(self):
        """Retorna estatísticas simples do índice (usado pelos testes)."""
        return {
            "total_vectors": int(self.index.ntotal),
            "dimension": int(self.index.d)
        }

    def save(self):
        """Salva o índice FAISS e metadados (se path fornecido)."""
        if not self.path:
            log_info("⚠️ Nenhum path configurado para persistência. Chame FaissVectorStore(path=...)")
            return

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # salva índice binário
        try:
            faiss.write_index(self.index, self.path)
        except Exception as e:
            log_info(f"❌ Falha ao salvar índice FAISS: {e}")
            raise

        # salva metadados (arquivo .meta.npy)
        meta_path = f"{self.path}.meta.npy"
        try:
            # metadatas -> objeto numpy (usamos allow_pickle)
            np.save(meta_path, np.array(self.metadata, dtype=object), allow_pickle=True)
        except Exception as e:
            log_info(f"❌ Falha ao salvar metadados FAISS: {e}")
            raise

        log_info(f"💾 Índice FAISS salvo em: {self.path}")

    def load(self):
        """Carrega o índice FAISS e metadados (se existir)."""
        if not self.path or not os.path.exists(self.path):
            raise FileNotFoundError(f"Índice FAISS não encontrado em: {self.path}")

        # carrega índice
        self.index = faiss.read_index(self.path)

        # carrega metadatas se existir
        meta_path = f"{self.path}.meta.npy"
        if os.path.exists(meta_path):
            try:
                arr = np.load(meta_path, allow_pickle=True)
                # converter para lista de dicts (se possível)
                self.metadata = arr.tolist() if hasattr(arr, "tolist") else list(arr)
            except Exception as e:
                log_info(f"⚠️ Falha ao carregar metadados FAISS: {e}")
                self.metadata = []
        else:
            self.metadata = []

        log_info(f"📂 Índice FAISS carregado de: {self.path}")


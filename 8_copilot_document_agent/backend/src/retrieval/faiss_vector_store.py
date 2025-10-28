import faiss
import numpy as np
import os
import json
from typing import List, Optional
from src.core.logger import log_info

class FaissVectorStore:
    """FAISS index simples com armazenamento de metadados e persistência usando JSON para metadados."""

    def __init__(self, embedding_dim: int = 1536, path: Optional[str] = None):
        """
        :param embedding_dim: dimensão esperada dos embeddings
        :param path: caminho do arquivo para persistir o índice (FAISS binary)
        """
        self.embedding_dim = embedding_dim
        self.path = path if path else None
        # cria índice em memória
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata: List[dict] = []

        # tenta carregar se os arquivos existem
        if self.path:
            index_file = self.path
            meta_file = f"{self.path}.meta.json"
            if os.path.exists(index_file) or os.path.exists(meta_file):
                try:
                    self.load()
                except Exception as e:
                    log_info(f"⚠️ Falha ao carregar índice FAISS de {self.path}: {e}")

    def add_embeddings(self, vectors: List[List[float]], metadatas: Optional[List[dict]] = None):
        if not vectors:
            return

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

        # adiciona metadados
        if metadatas:
            if len(metadatas) != len(vectors):
                log_info("⚠️ Número de metadatas diferente do número de vetores. Ajustando pelo mínimo.")
            self.metadata.extend(metadatas[:len(vectors)])

        log_info(f"✅ Adicionados {array.shape[0]} vetores ao FAISS.")

    def search(self, query_vector: List[float], k: int = 5):
        q = np.array([query_vector], dtype="float32")
        if q.shape[1] != self.index.d:
            raise ValueError(f"Dimensão do vetor de consulta incorreta. Esperado {self.index.d}, recebido {q.shape[1]}")

        D, I = self.index.search(q, k)
        return D, I

    def get_stats(self):
        return {
            "total_vectors": int(self.index.ntotal),
            "dimension": int(self.index.d)
        }

    def save(self):
        """Salva índice FAISS e metadados em JSON"""
        if not self.path:
            log_info("⚠️ Nenhum path configurado para persistência. Chame FaissVectorStore(path=...)")
            return

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # salva índice FAISS
        try:
            faiss.write_index(self.index, self.path)
        except Exception as e:
            log_info(f"❌ Falha ao salvar índice FAISS: {e}")
            raise

        # salva metadados como JSON
        meta_path = f"{self.path}.meta.json"
        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_info(f"❌ Falha ao salvar metadados FAISS: {e}")
            raise

        log_info(f"💾 Índice FAISS salvo em: {self.path} com {len(self.metadata)} metadados.")

    def load(self):
        """Carrega índice FAISS e metadados de JSON"""
        if not self.path or not os.path.exists(self.path):
            raise FileNotFoundError(f"Índice FAISS não encontrado em: {self.path}")

        # carrega índice FAISS
        try:
            self.index = faiss.read_index(self.path)
        except Exception as e:
            log_info(f"❌ Falha ao carregar índice FAISS: {e}")
            raise

        # carrega metadados JSON
        meta_path = f"{self.path}.meta.json"
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                log_info(f"⚠️ Falha ao carregar metadados FAISS: {e}")
                self.metadata = []
        else:
            self.metadata = []

        log_info(f"📂 Índice FAISS carregado de: {self.path}")
        log_info(f"📦 FAISS carregado com {self.index.ntotal} vetores e {len(self.metadata)} metadados.")
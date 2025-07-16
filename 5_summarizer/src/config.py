import os
from dotenv import load_dotenv
load_dotenv()

# Caminho onde o ChromaDB vai persistir os dados
CHROMA_PERSIST_PATH = "./db/chroma_persist"

# Nome da collection usada para embeddings
VECTOR_STORE_COLLECTION = "rag_collection"

# Modelo padrão de embedding (caso você queira trocar futuramente)
EMBEDDING_MODEL = "default"

USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
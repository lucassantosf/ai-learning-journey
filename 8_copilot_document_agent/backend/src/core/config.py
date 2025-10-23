import os
from dotenv import load_dotenv

load_dotenv()

class Config: 
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/faiss_index")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))

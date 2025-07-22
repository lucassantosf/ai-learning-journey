import os
from dotenv import load_dotenv
load_dotenv()

# Path where ChromaDB will persist data
CHROMA_PERSIST_PATH = "./db/chroma_persist"

# Collection name used for embeddings
VECTOR_STORE_COLLECTION = "rag_collection"

# Default embedding model (in case you want to change it in the future)
EMBEDDING_MODEL = "default"

USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes import health, upload, feedback, retrain
from pathlib import Path
import json, os

# Imports dos agents e rotas
from agent.embedder import Embedder
from agent.vector_store import VectorStore
from agent.prompt_engine import PromptEngine
from agent.document_agent import DocumentAgent

api = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)
 
# Configuração de CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js local
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos: GET, POST, etc.
    allow_headers=["*"],  # Permite todos os headers
)

# Rotas
api.include_router(health.router)
api.include_router(upload.router)
api.include_router(feedback.router)
api.include_router(retrain.router)

@api.on_event("startup")
def startup_event():
    print("🚀 Iniciando aplicação e carregando recursos...")

    mode = os.getenv("VECTOR_STORE_MODE", "json").lower()
    api.state.embedder = Embedder()
    api.state.vector_store = VectorStore(mode=mode)
    api.state.prompt_engine = PromptEngine()
    api.state.document_agent = DocumentAgent()

    if mode == "json":
        DATASET_FILE = Path(__file__).resolve().parent.parent / "dataset" / "embeddings.json"
        if DATASET_FILE.exists():
            with open(DATASET_FILE, "r", encoding="utf-8") as f:
                dataset = json.load(f)
                for embedding, metadata in dataset:
                    api.state.vector_store.add(embedding, metadata)
            print(f"✅ Dataset JSON carregado com {len(dataset)} embeddings")
        else:
            print("⚠️ Nenhum dataset JSON encontrado.")
    elif mode == "sqlite":
        api.state.vector_store.load_from_sqlite()
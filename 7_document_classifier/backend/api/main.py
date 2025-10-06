from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes import health, upload
from api.core.database import SessionLocal
from sqlalchemy.orm import Session
from pathlib import Path
import json

# Imports dos agents e rotas
from agent.embedder import Embedder
from agent.vector_store import VectorStore
from agent.prompt_engine import PromptEngine
from agent.document_agent import DocumentAgent
from api.routes import upload

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

@api.on_event("startup")
def startup_event():
    print("🚀 Iniciando aplicação e carregando recursos...")

    # Embedder singleton
    api.state.embedder = Embedder()

    # Vector store singleton
    vs = VectorStore()
    DATASET_FILE = Path(__file__).resolve().parent.parent / "dataset" / "embeddings.json"
    if DATASET_FILE.exists():
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            dataset = json.load(f)
            for embedding, metadata in dataset:
                if isinstance(embedding, list) and len(embedding) == 1 and isinstance(embedding[0], list):
                    embedding = embedding[0]
                elif isinstance(embedding, float):
                    embedding = [embedding]
                vs.add(embedding, metadata)
        print(f"✅ Dataset carregado: {len(dataset)} embeddings")
    else:
        print("⚠️ Nenhum dataset encontrado, prosseguindo vazio")

    api.state.vector_store = vs
    api.state.prompt_engine = PromptEngine()
    api.state.document_agent = DocumentAgent()
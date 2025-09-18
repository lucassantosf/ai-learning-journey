from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes import health, upload

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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import health, upload

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js local
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos: GET, POST, etc.
    allow_headers=["*"],  # Permite todos os headers
)

# Rotas
app.include_router(health.router)
app.include_router(upload.router)
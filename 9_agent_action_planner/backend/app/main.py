# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_agent import router as agent_router
from app.models.base import Base, engine

app = FastAPI(
    title="AgentFlow API",
    version="0.1.0",
    description="Backend base do agente com memória e planejamento."
)

# Middleware CORS (caso queira integrar com frontend depois)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["Agent"])

# Healthcheck root
@app.get("/")
def root():
    return {"status": "ok", "message": "AgentFlow API is running..."}

@app.on_event("startup")
def on_startup():
    print("🔧 Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
from fastapi import FastAPI
from app.api.routes_health import router as health_router

app = FastAPI(
    title="AgentFlow API",
    version="0.1.0",
    description="Backend base do agente com memória e planejamento."
)

# Rotas
app.include_router(health_router, prefix="/api/v1")

# Healthcheck root
@app.get("/")
def root():
    return {"status": "ok", "message": "AgentFlow API is running..."}
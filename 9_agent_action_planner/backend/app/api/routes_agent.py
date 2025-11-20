from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, Dict, List

from app.services.agent_service import AgentService
from app.core.dependencies import get_agent_service

router = APIRouter(tags=["Agent"])

# ---------------------------
# Request/Response Schemas
# ---------------------------

class PlanRequest(BaseModel):
    prompt: str


class ExecuteRequest(BaseModel):
    plan_id: int


# ---------------------------
# Endpoints
# ---------------------------

@router.post("/plan")
async def create_plan(
    user_request: PlanRequest,
    agent: AgentService = Depends(get_agent_service)
):
    return await agent.create_plan(user_request.prompt)

@router.post("/execute")
async def execute_plan(
    request: ExecuteRequest,
    agent: AgentService = Depends(get_agent_service)
):
    """
    Executa um plano passo a passo.
    """
    result = await agent.execute_plan(request.plan_id)
    return {"result": result}


@router.get("/memory")
async def get_memory(
    agent: AgentService = Depends(get_agent_service)
):
    """
    Retorna o histórico do agente (memory_logs).
    """
    memory = agent.get_memory()
    return {"memory": memory}


# ---------------------------
# WebSocket — Progresso em tempo real
# ---------------------------

@router.websocket("/ws/progress")
async def ws_progress(
    websocket: WebSocket,
    agent: AgentService = Depends(get_agent_service)
):
    """
    WebSocket para enviar atualizações de execução em tempo real.
    """
    await websocket.accept()
    try:
        async for update in agent.stream_execution_updates():
            await websocket.send_json(update)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
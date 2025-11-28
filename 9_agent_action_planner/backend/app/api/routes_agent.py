from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, Dict, List
from datetime import datetime

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
# Endpoints REST
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
    Agora totalmente compatível com o novo Executor,
    enviando step_start / step_update / step_complete corretamente.
    """
    await websocket.accept()

    connection_active = True
    event_count = 0

    try:
        print("WebSocket conectado. Iniciando stream...")

        async for update in agent.stream_execution_updates():

            # Defender — se desconectado, parar imediatamente
            if not connection_active:
                print("WS desconectado, interrompendo stream")
                break

            try:
                print(f"[WS] Enviando update: {update}")
                await websocket.send_json(update)
                event_count += 1

                if event_count % 10 == 0:
                    print(f"[WS] {event_count} eventos enviados")

            except Exception as send_error:
                print(f"[WS] Erro ao enviar evento: {send_error}")

                # Tentativa de enviar mensagem de erro
                try:
                    await websocket.send_json({
                        "type": "websocket_send_error",
                        "error": str(send_error),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass

    except WebSocketDisconnect:
        print("Cliente desconectou do WebSocket")
        connection_active = False

    except Exception as e:
        print(f"[WS] Erro crítico: {e}")

        # Tentativa de avisar o cliente
        try:
            await websocket.send_json({
                "type": "stream_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            pass

        await websocket.close(code=1011)

    finally:
        print(f"[WS] Finalizado. Total de eventos enviados: {event_count}")
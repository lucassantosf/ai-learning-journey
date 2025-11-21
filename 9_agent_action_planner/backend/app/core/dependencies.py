from fastapi import Depends

from app.services.memory_sqlite import SQLiteMemory
from app.services.planner import Planner
from app.services.executor import Executor
from app.services.agent_service import AgentService
from app.models.base import get_db_session
from app.core.config import settings


# ============================================================
# SINGLETONS
# ============================================================

# Planner pode ser singleton
planner_singleton = Planner(model_name=settings.OPENAI_MODEL)


# ============================================================
# POR REQUEST
# ============================================================

def get_memory(db=Depends(get_db_session)) -> SQLiteMemory:
    return SQLiteMemory(db)


def get_planner() -> Planner:
    return planner_singleton


def get_executor(
    db=Depends(get_db_session),
    memory: SQLiteMemory = Depends(get_memory)
) -> Executor:
    """
    Executor NÃO PODE ser singleton.
    Ele depende de db, memory e usa stream_buffer interno.
    Logo deve ser instância por request.
    """
    return Executor(db=db, memory=memory)


# ============================================================
# AGENT SERVICE
# ============================================================

def get_agent_service(
    db=Depends(get_db_session),
    planner: Planner = Depends(get_planner),
    memory: SQLiteMemory = Depends(get_memory),
    executor: Executor = Depends(get_executor),
):
    """
    AgentService pode ser criado por request — é leve.
    Ele só faz orquestração.
    """
    return AgentService(
        db=db,
        planner=planner,
        memory=memory,
        executor=executor,
        tools=[],
    )
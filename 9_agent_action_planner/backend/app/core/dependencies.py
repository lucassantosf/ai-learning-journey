from fastapi import Depends

from app.services.memory_sqlite import SQLiteMemory
from app.services.planner import Planner
from app.services.executor import Executor
from app.services.agent_service import AgentService
from app.models.base import get_db_session
from app.core.config import settings


# -----------------------------
# SINGLETONS / CONFIG
# -----------------------------

def get_planner() -> Planner:
    return Planner(model_name=settings.OPENAI_MODEL)


# -----------------------------
# INSTÂNCIAS POR REQUEST
# -----------------------------

def get_memory(db = Depends(get_db_session)) -> SQLiteMemory:
    """
    A memória usa a MESMA sessão do banco.
    """
    return SQLiteMemory(db)


def get_executor(
    db = Depends(get_db_session),
    memory: SQLiteMemory = Depends(get_memory)
) -> Executor:
    return Executor(db=db, memory=memory)


def get_agent_service(
    db = Depends(get_db_session),
    memory: SQLiteMemory = Depends(get_memory),
    planner: Planner = Depends(get_planner),
    executor: Executor = Depends(get_executor),
) -> AgentService:

    return AgentService(
        db=db,
        planner=planner,
        memory=memory,
        executor=executor,
        tools=[],
    )
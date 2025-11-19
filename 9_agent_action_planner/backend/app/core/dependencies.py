from functools import lru_cache
from app.core.config import settings
from app.services.memory_sqlite import SQLiteMemory
from app.services.planner import Planner
from app.services.executor import Executor
from app.services.agent_service import AgentService
from app.models.base import get_db_session


@lru_cache
def get_memory() -> SQLiteMemory:
    return SQLiteMemory(settings.DATABASE_URL)


@lru_cache
def get_planner() -> Planner:
    return Planner(model_name=settings.OPENAI_MODEL)


@lru_cache
def get_executor() -> Executor:
    db = next(get_db_session())
    memory = get_memory()
    return Executor(db=db, memory=memory)


def get_agent_service() -> AgentService:
    db = next(get_db_session())
    return AgentService(
        db=db,
        planner=get_planner(),
        memory=get_memory(),
        executor=get_executor(),
        tools=[],
    )
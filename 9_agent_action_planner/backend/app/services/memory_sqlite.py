from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models.db_models import MemoryLog, Plan, Step
from app.models.base import Base

class SQLiteMemory:
    """
    Serviço responsável por persistir e recuperar memória do agente,
    incluindo logs, planos e passos.
    """

    def __init__(self, db_url: str):
        if db_url.startswith("sqlite:///"):
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        self.engine = create_async_engine(db_url, echo=False, future=True)

        self.SessionLocal = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )

    # ------------------------------------------------------------------
    # DATABASE INITIALIZATION
    # ------------------------------------------------------------------
    async def init_db(self):
        """Cria tabelas no SQLite se não existirem."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # ------------------------------------------------------------------
    # MEMORY LOGS
    # ------------------------------------------------------------------
    async def add_memory(self, message: str) -> MemoryLog:
        """Salva uma entrada de memória."""
        async with self.SessionLocal() as session:
            log = MemoryLog(message=message)
            session.add(log)
            await session.commit()
            await session.refresh(log)
            return log

    async def list_memory(self, limit: int = 50) -> List[MemoryLog]:
        """Retorna as últimas memórias (limitadas)."""
        async with self.SessionLocal() as session:
            stmt = select(MemoryLog).order_by(MemoryLog.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    # ------------------------------------------------------------------
    # PLANS
    # ------------------------------------------------------------------
    async def create_plan(self, title: str) -> Plan:
        """Cria um novo plano."""
        async with self.SessionLocal() as session:
            plan = Plan(title=title)
            session.add(plan)
            await session.commit()
            await session.refresh(plan)
            return plan

    async def get_plan(self, plan_id: int) -> Optional[Plan]:
        async with self.SessionLocal() as session:
            stmt = select(Plan).where(Plan.id == plan_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def list_plans(self) -> List[Plan]:
        async with self.SessionLocal() as session:
            stmt = select(Plan).order_by(Plan.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

    # ------------------------------------------------------------------
    # STEPS
    # ------------------------------------------------------------------
    async def add_step(
        self,
        plan_id: int,
        description: str,
        tool: Optional[str] = None,
        status: str = "pending",
    ) -> Step:
        """Adiciona um passo ao plano."""
        async with self.SessionLocal() as session:
            step = Step(plan_id=plan_id, description=description, tool=tool, status=status)
            session.add(step)
            await session.commit()
            await session.refresh(step)
            return step

    async def update_step_status(self, step_id: int, status: str):
        """Atualiza status de um passo."""
        async with self.SessionLocal() as session:
            stmt = select(Step).where(Step.id == step_id)
            result = await session.execute(stmt)
            step = result.scalars().first()
            if step:
                step.status = status
                await session.commit()

    async def list_steps(self, plan_id: int) -> List[Step]:
        """Retorna todos os passos de um plano."""
        async with self.SessionLocal() as session:
            stmt = select(Step).where(Step.plan_id == plan_id)
            result = await session.execute(stmt)
            return result.scalars().all()
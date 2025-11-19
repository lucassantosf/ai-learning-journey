from typing import Any, Dict, List, AsyncGenerator
from datetime import datetime

from app.services.planner import Planner
from app.services.executor import Executor
from app.services.memory_sqlite import SQLiteMemory
from app.models.db_models import Plan, Step


class AgentService:
    """
    Orquestra Planner, Executor, DB e Memória.
    Usada diretamente pela API.
    """

    def __init__(self, db, planner: Planner, memory: SQLiteMemory, executor: Executor, tools=None):
        self.db = db
        self.planner = planner
        self.memory = memory
        self.executor = executor
        self.tools = tools or []
    
    # -----------------------
    # PLANEJAMENTO
    # -----------------------
    async def create_plan(self, prompt: str) -> Dict[str, Any]:

        generated_plan = await self.planner.generate_plan(prompt)

        plan = Plan(
            prompt=prompt,
            created_at=datetime.utcnow(),
            status="created"
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        for idx, step_text in enumerate(generated_plan["steps"], start=1):
            step = Step(
                plan_id=plan.id,
                order=idx,
                description=step_text,
                status="pending"
            )
            self.db.add(step)

        self.db.commit()

        self.memory.add_log("planner_output", generated_plan)

        return {
            "plan_id": plan.id,
            "steps": generated_plan["steps"],
            "status": plan.status
        }

    # -----------------------
    # EXECUÇÃO
    # -----------------------
    async def execute_plan(self, plan_id: int) -> Dict[str, Any]:

        steps = (
            self.db.query(Step)
            .filter_by(plan_id=plan_id)
            .order_by(Step.order.asc())
            .all()
        )

        if not steps:
            return {"error": "Plan not found or no steps exist"}

        results = []

        for step in steps:
            result = await self.executor.run_step(step)
            results.append({
                "step": step.order,
                "description": step.description,
                "result": result
            })

            self.db.commit()

        self.memory.add_log("execution_summary", results)

        plan = self.db.query(Plan).filter_by(id=plan_id).first()
        plan.status = "completed"
        self.db.commit()

        return {
            "plan_id": plan_id,
            "results": results
        }

    # -----------------------
    # MEMÓRIA
    # -----------------------
    def get_memory(self):
        return self.memory.get_logs()

    # -----------------------
    # STREAMING
    # -----------------------
    async def stream_execution_updates(self):
        async for event in self.executor.stream():
            yield event
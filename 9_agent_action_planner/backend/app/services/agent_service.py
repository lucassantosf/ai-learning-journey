from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio

from app.services.planner import Planner
from app.services.executor import Executor
from app.services.memory_sqlite import SQLiteMemory
from app.models.db_models import Plan, Step


class AgentService:
    """
    Orquestrador principal.
    Coordena Planner → Banco → Executor → Memória.
    """

    def __init__(
        self,
        db: Session,
        planner: Planner,
        memory: SQLiteMemory,
        executor: Executor,
        tools: Optional[List[Any]] = None
    ):
        self.db = db
        self.planner = planner
        self.memory = memory
        self.executor = executor
        self.tools = tools or []

        # Task de execução do plano atual
        self._current_execution_task: Optional[asyncio.Task] = None

        # Integra ferramentas
        if hasattr(self.executor, "set_tools"):
            self.executor.set_tools(self.tools)

    # ------------------------------------------------------
    # PLANEJAMENTO
    # ------------------------------------------------------
    async def create_plan(self, prompt: str) -> Dict[str, Any]:
        generated = await self.planner.generate_plan(prompt)

        try:
            with self.db.begin():
                plan = Plan(
                    prompt=prompt,
                    created_at=datetime.utcnow(),
                    status="created"
                )
                self.db.add(plan)
                self.db.flush()

                for idx, text in enumerate(generated["steps"], start=1):
                    step = Step(
                        plan_id=plan.id,
                        order=idx,
                        description=text,
                        status="pending",
                        created_at=datetime.utcnow(),
                    )
                    self.db.add(step)

            # Log na memória
            self.memory.add_log("planner_output", {
                "plan_id": plan.id,
                "prompt": prompt,
                "generated": generated
            })

            return {
                "plan_id": plan.id,
                "steps": generated["steps"],
                "status": plan.status,
            }

        except Exception as e:
            try:
                self.db.rollback()
            except Exception:
                pass
            raise RuntimeError(f"Failed to create plan: {e}")

    # ------------------------------------------------------
    # EXECUÇÃO DO PLANO
    # ------------------------------------------------------
    async def execute_plan(self, plan_id: int) -> Dict[str, Any]:
        """
        NÃO executa os steps diretamente.
        Apenas dispara uma task assíncrona no executor,
        permitindo que o streaming aconteça em paralelo.
        """

        plan = self.db.query(Plan).filter_by(id=plan_id).first()
        if not plan:
            return {"error": "Plan not found"}

        steps: List[Step] = (
            self.db.query(Step)
            .filter_by(plan_id=plan_id)
            .order_by(Step.order.asc())
            .all()
        )
        if not steps:
            return {"error": "Plan has no steps"}

        # Atualiza status
        plan.status = "in_progress"
        plan.updated_at = datetime.utcnow()
        self.db.commit()

        # Se já existe uma task anterior, cancelamos
        if self._current_execution_task and not self._current_execution_task.done():
            self._current_execution_task.cancel()

        # --- AGORA SIM: execução real rodando em paralelo ---
        async def _run_and_store():
            try:
                for step in steps:
                    # Marca início
                    step.status = "running"
                    step.updated_at = datetime.utcnow()
                    self.db.commit()

                    try:
                        result = await self.executor.run_step(step)

                        step.status = "completed"
                        step.result = (
                            result if isinstance(result, str) else str(result)
                        )
                        step.updated_at = datetime.utcnow()
                        self.db.commit()

                    except Exception as step_err:
                        step.status = "failed"
                        step.result = str(step_err)
                        step.updated_at = datetime.utcnow()
                        self.db.commit()
                        continue

                # Finaliza plano
                plan.status = "completed"
                plan.updated_at = datetime.utcnow()
                self.db.commit()

            except Exception as e:
                try:
                    self.db.rollback()
                except Exception:
                    pass
                print(f"[AgentService] Erro interno na execução do plano: {e}")

            finally:
                # IMPORTANTE: avisa executor para parar o stream
                self.executor.close_stream()

        # Cria a task assíncrona que rodará em paralelo ao WebSocket
        self._current_execution_task = asyncio.create_task(_run_and_store())

        return {
            "plan_id": plan_id,
            "status": "started",
            "message": "Execução iniciada. Veja progressos via WebSocket."
        }

    # ------------------------------------------------------
    # MEMÓRIA
    # ------------------------------------------------------
    def get_memory(self) -> List[Dict[str, Any]]:
        return self.memory.get_logs()

    # ------------------------------------------------------
    # STREAMING
    # ------------------------------------------------------
    async def stream_execution_updates(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Apenas repassa o stream do executor.
        """
        print("[AgentService] stream_execution_updates iniciado...")

        if not hasattr(self.executor, "stream"):
            raise RuntimeError("Executor does not support streaming")

        async for event in self.executor.stream():
            print(f"[AgentService] Evento → {event}")
            yield event

    # ------------------------------------------------------
    # AUTO-REFLEXÃO (preservado)
    # ------------------------------------------------------
    def _simple_reflection(self, step: Step, result: Any, success: bool) -> Dict[str, Any]:
        if isinstance(result, str):
            rtext = result
        else:
            try:
                rtext = str(result)
            except Exception:
                rtext = "<unserializable result>"

        if success:
            summary = f"Step {step.order} completed successfully."
            suggestion = "No immediate action required."
        else:
            summary = f"Step {step.order} failed."
            if "timeout" in rtext.lower():
                suggestion = "Consider increasing timeout or retry later."
            elif "error" in rtext.lower() or "traceback" in rtext.lower():
                suggestion = "Check error message and retry; consider adding validation."
            else:
                suggestion = "Investigate the step result and consider retrying."

        return {
            "plan_id": step.plan_id,
            "step": step.order,
            "success": success,
            "summary": summary,
            "detail": rtext,
            "suggestion": suggestion,
            "timestamp": datetime.utcnow().isoformat()
        }
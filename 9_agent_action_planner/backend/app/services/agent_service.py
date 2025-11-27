from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.planner import Planner
from app.services.executor import Executor
from app.services.memory_sqlite import SQLiteMemory
from app.models.db_models import Plan, Step


class AgentService:
    """
    Serviço orquestrador principal.
    Coordena Planner → Banco → Executor → Memória.
    Direto para a API.
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

        # Integra ferramentas no executor, caso ele suporte
        if hasattr(self.executor, "set_tools"):
            self.executor.set_tools(self.tools)

    # ------------------------------------------------------
    # PLANEJAMENTO
    # ------------------------------------------------------
    async def create_plan(self, prompt: str) -> Dict[str, Any]:
        """
        Gera um plano via LLM, salva no banco e registra memória.
        """

        generated = await self.planner.generate_plan(prompt)

        try:
            with self.db.begin():
                plan = Plan(
                    prompt=prompt,
                    created_at=datetime.utcnow(),
                    status="created"
                )
                self.db.add(plan)

                # flush para garantir que plan.id exista antes de criar steps
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

            # Log na memória (persistência auxiliar)
            # Guarda o plan gerado (estrutura) e o prompt
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
            # tentativa de rollback caso algo falhe
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
        Executa todos os steps de um plano de forma sequencial,
        registrando status/resultado/reflexões em memória.
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

        execution_results = []

        # marca o plano como em progresso
        plan.status = "in_progress"
        plan.updated_at = datetime.utcnow()
        self.db.commit()

        try:
            for step in steps:
                # --- antes de executar: marcar running e logar evento ---
                step.status = "running"
                step.updated_at = datetime.utcnow()
                self.db.commit()

                self.memory.add_log("step_started", {
                    "plan_id": plan_id,
                    "step": step.order,
                    "description": step.description,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # executar passo (executor deve retornar string / dict / qualquer)
                try:
                    result = await self.executor.run_step(step)

                    # salvar resultado e status
                    step.status = "completed"
                    step.result = result if isinstance(result, str) else str(result)
                    step.updated_at = datetime.utcnow()
                    self.db.commit()

                    # log por step
                    self.memory.add_log("step_result", {
                        "plan_id": plan_id,
                        "step": step.order,
                        "description": step.description,
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    execution_results.append({
                        "step": step.order,
                        "description": step.description,
                        "result": result
                    })

                    # auto-reflexão simples para step concluído
                    reflection = self._simple_reflection(step, result, success=True)
                    self.memory.add_log("reflection", reflection)

                except Exception as step_err:
                    # marca falha no step
                    step.status = "failed"
                    step.result = str(step_err)
                    step.updated_at = datetime.utcnow()
                    self.db.commit()

                    # log de falha
                    self.memory.add_log("step_failed", {
                        "plan_id": plan_id,
                        "step": step.order,
                        "description": step.description,
                        "error": str(step_err),
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    execution_results.append({
                        "step": step.order,
                        "description": step.description,
                        "error": str(step_err)
                    })

                    # auto-reflexão simples para step com erro
                    reflection = self._simple_reflection(step, str(step_err), success=False)
                    self.memory.add_log("reflection", reflection)

                    # continuar para próximos steps (não abortar)
                    continue

            # finaliza plano
            plan.status = "completed"
            plan.updated_at = datetime.utcnow()
            self.db.commit()

            # Log geral na memória
            self.memory.add_log("execution_summary", {
                "plan_id": plan_id,
                "results": execution_results,
                "completed_at": datetime.utcnow().isoformat()
            })

            return {
                "plan_id": plan_id,
                "results": execution_results
            }

        except Exception as e:
            try:
                self.db.rollback()
            except Exception:
                pass
            raise RuntimeError(f"Error while executing plan {plan_id}: {e}")

    # ------------------------------------------------------
    # MEMÓRIA
    # ------------------------------------------------------
    def get_memory(self) -> List[Dict[str, Any]]:
        """
        Retorna logs do SQLiteMemory.
        """
        return self.memory.get_logs()

    # ------------------------------------------------------
    # STREAMING (caso executor suporte)
    # ------------------------------------------------------
    async def stream_execution_updates(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Repasse do stream do executor.
        Útil para SSE / Websockets.
        """
        print("stream_execution_updates iniciado...")  # Log de debug

        if not hasattr(self.executor, "stream"):
            print("Executor não suporta streaming!")  # Log de erro
            raise RuntimeError("Executor does not support streaming")

        try:
            async for event in self.executor.stream():
                print(f"Evento recebido: {event}")  # Log de cada evento
                yield event

        except Exception as e:
            print(f"Erro durante stream_execution_updates: {e}")  # Log de erro
            yield {
                'type': 'stream_error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    # ------------------------------------------------------
    # AUTO-REFLEXÃO (simples)
    # ------------------------------------------------------
    def _simple_reflection(self, step: Step, result: Any, success: bool) -> Dict[str, Any]:
        """
        Gera uma reflexão simples baseada no resultado do step.
        Regras:
         - se success True => breve nota do que deu certo
         - se success False => razão curta do erro + sugestão básica
        """
        # Normaliza resultado para string curta
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
            # heurística simples para sugerir ação
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
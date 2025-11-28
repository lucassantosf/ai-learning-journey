from typing import Dict, Any, AsyncGenerator, Optional, List
from datetime import datetime
import asyncio

from langchain_openai import ChatOpenAI

from app.models.db_models import Step
from app.tools.base import ToolRegistry

# Sentinel para encerrar stream()
_SENTINEL = {"type": "__stream_end__"}


class Executor:
    """
    Executor responsável por:
    - Executar steps sequencialmente
    - Gerar eventos para WebSocket via fila assíncrona
    - Emitir heartbeat quando não tiver eventos
    - Finalizar stream com sentinel
    """

    def __init__(self, db, memory):
        self.db = db
        self.memory = memory

        # Mantive o seu modelo exatamente como estava:
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            timeout=180
        )

        # Fila de eventos (produtor -> consumidor/stream)
        self._queue: asyncio.Queue = asyncio.Queue()

        # Opcional: referência para cancelar execução de plano
        self._current_task: Optional[asyncio.Task] = None

    # =====================================================================
    # PRODUÇÃO DE EVENTOS
    # =====================================================================

    def _enqueue(self, event: Dict[str, Any]) -> None:
        """
        Coloca um evento na fila. O stream() é o consumidor.
        """
        try:
            print(f"[Executor._enqueue] {event}")
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            print("[Executor._enqueue] Queue full, evento perdido:", event)

    # =====================================================================
    # EXECUÇÃO DE UM STEP (PRODUTOR)
    # =====================================================================

    async def run_step(self, step: Step) -> Dict[str, Any]:
        """
        Executa um step com emissão de múltiplos eventos.
        Não limpa a fila (isso derruba eventos).
        """
        print(f"[Executor] Iniciando step {step.order}")

        # Evento inicial
        self._enqueue({
            "type": "step_start",
            "step": step.order,
            "description": step.description,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {"plan_id": step.plan_id},
        })

        try:
            # Progress 25%
            self._enqueue({
                "type": "step_progress",
                "step": step.order,
                "progress": "25%",
                "message": "Preparando execução do passo...",
                "timestamp": datetime.utcnow().isoformat()
            })

            # Seleção da ferramenta
            tool = await self._select_tool(step.description)

            # Progress 50%
            self._enqueue({
                "type": "step_progress",
                "step": step.order,
                "progress": "50%",
                "message": f"Ferramenta selecionada: {tool.__class__.__name__ if tool else 'Nenhuma'}",
                "timestamp": datetime.utcnow().isoformat()
            })

            # Execução real
            if tool:
                result = await tool.run(step.description)
            else:
                result = await self._run_llm(step.description)

            # Evento final
            self._enqueue({
                "type": "step_complete",
                "step": step.order,
                "result": result,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })

            return result

        except Exception as e:
            err = str(e)
            print(f"[Executor] Erro no step {step.order}: {err}")

            self._enqueue({
                "type": "step_error",
                "step": step.order,
                "error": err,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            })

            raise

    # =====================================================================
    # STREAM (CONSUMIDOR)
    # =====================================================================

    async def stream(self, idle_timeout: float = 0.5) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consumidor do queue — envia eventos ao WebSocket.
        Se a fila ficar vazia por X segundos, envia heartbeat.
        """
        print("[Executor.stream] Stream iniciado")

        while True:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=idle_timeout)

                if (
                    event is _SENTINEL or
                    (isinstance(event, dict) and event.get("type") == _SENTINEL["type"])
                ):
                    print("[Executor.stream] Sentinel recebido, encerrando.")
                    break

                yield event

            except asyncio.TimeoutError:
                continue
                # Heartbeat
                # yield {
                #     "type": "heartbeat",
                #     "message": "Mantendo conexão ativa",
                #     "timestamp": datetime.utcnow().isoformat(),
                #     "queue_size_estimate": self._queue.qsize()
                # }

            except Exception as e:
                print(f"[Executor.stream] Erro: {e}")
                yield {
                    "type": "stream_error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                await asyncio.sleep(0.5)

    def close_stream(self):
        """Fecha o stream com sentinel."""
        try:
            self._queue.put_nowait(_SENTINEL)
        except Exception as e:
            print(f"[Executor.close_stream] erro ao enviar sentinel: {e}")

    # =====================================================================
    # EXECUÇÃO DE UM PLANO COMPLETO
    # =====================================================================

    async def run_plan(self, steps: List[Step]):
        """
        Executa todos os steps sequencialmente.
        Deve rodar em task separada do WebSocket.
        """
        try:
            for step in steps:
                await self.run_step(step)
        finally:
            # Finalização garantida
            self.close_stream()

    # =====================================================================
    # SELEÇÃO DE TOOL
    # =====================================================================

    async def _select_tool(self, text: str):
        tools = ToolRegistry.all()
        tool_names = ", ".join(tools.keys())

        system_prompt = "Você é um roteador de ferramentas..."
        user_prompt = (
            f"Texto: {text}\n"
            f"Ferramentas disponíveis: {tool_names}\n"
            "Responda SOMENTE com o nome da ferramenta ou 'none'."
        )

        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        tool_name = response.content.strip().lower()

        return tools.get(tool_name)

    # =====================================================================
    # EXECUÇÃO VIA LLM (SE NÃO TIVER TOOL)
    # =====================================================================

    async def _run_llm(self, text: str) -> str:
        response = await self.llm.ainvoke([
            {"role": "system", "content": "Execute a tarefa de forma concisa e prática."},
            {"role": "user", "content": text}
        ])
        return response.content.strip()
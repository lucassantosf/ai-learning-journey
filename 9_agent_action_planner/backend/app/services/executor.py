from typing import Dict, Any, AsyncGenerator
from datetime import datetime

from langchain_openai import ChatOpenAI

from app.models.db_models import Step
from app.tools.base import ToolRegistry


class Executor:
    """
    Executa cada passo do plano.
    - Identifica intenção do passo
    - Seleciona ferramenta apropriada (via ToolRegistry)
    - Executa e grava resultado
    - Envia updates ao stream (WebSocket)
    """

    def __init__(self, db, memory):
        self.db = db
        self.memory = memory
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, timeout=180)

        # Buffer para streaming (WebSocket)
        self._stream_buffer = []  # lista de dicts enviados incrementalmente

    # ------------------------------------------
    # STREAMING PARA O WEBSOCKET
    # ------------------------------------------
    def _push_stream(self, event: Dict[str, Any]):
        """
        Adiciona evento no buffer para o WebSocket.
        Adiciona logs para debug.
        """
        print(f"Adicionando evento ao buffer: {event}")  # Log de debug
        self._stream_buffer.append(event)
        print(f"Buffer após adição: {self._stream_buffer}")  # Log de estado do buffer

    # ------------------------------------------
    # EXECUTAR UM ÚNICO PASSO
    # ------------------------------------------
    async def run_step(self, step: Step) -> Dict[str, Any]:
        """
        Executa um passo usando LLM + ferramentas.
        Envia eventos de progresso via WebSocket.
        """
        # Log de início da execução do passo
        print(f"Iniciando execução do passo {step.order}")

        # Evento de início do passo - IMPORTANTE: Garantir que seja adicionado ao buffer
        self._push_stream({
            "type": "step_start",
            "step": step.order,
            "description": step.description,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "plan_id": step.plan_id,
                "total_steps": getattr(step, 'total_steps', None)
            }
        })
        print(f"Evento de início do passo {step.order} adicionado ao buffer")

        try:
            # Evento de progresso inicial
            self._push_stream({
                "type": "step_progress",
                "step": step.order,
                "progress": "25%",
                "message": "Preparando execução do passo...",
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"Evento de progresso inicial do passo {step.order} adicionado ao buffer")

            # Identificar ferramenta
            tool = await self._select_tool(step.description)
            print(f"Ferramenta selecionada para o passo {step.order}: {tool}")

            # Evento de seleção de ferramenta
            self._push_stream({
                "type": "step_progress",
                "step": step.order,
                "progress": "50%",
                "message": f"Ferramenta selecionada: {tool.__class__.__name__ if tool else 'Nenhuma'}",
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"Evento de seleção de ferramenta do passo {step.order} adicionado ao buffer")

            # Execução da ferramenta ou LLM
            if tool:
                result = await tool.run(step.description)
            else:
                result = await self._run_llm(step.description)
            
            print(f"Resultado do passo {step.order}: {result}")

            # Evento de conclusão do passo
            self._push_stream({
                "type": "step_complete",
                "step": step.order,
                "result": result,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"Evento de conclusão do passo {step.order} adicionado ao buffer")

            return result

        except Exception as e:
            error_message = str(e)
            print(f"Erro no passo {step.order}: {error_message}")

            # Evento de erro
            self._push_stream({
                "type": "step_error",
                "step": step.order,
                "error": error_message,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"Evento de erro do passo {step.order} adicionado ao buffer")

            raise

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generator: retorna eventos em tempo real.
        """
        print("Método stream() iniciado. Buffer inicial:", self._stream_buffer)
        
        last_index = 0
        while True:
            # Log detalhado do estado atual
            print(f"Estado atual - Último índice: {last_index}, Tamanho do buffer: {len(self._stream_buffer)}")

            if last_index < len(self._stream_buffer):
                event = self._stream_buffer[last_index]
                print(f"Enviando evento: {event}")
                last_index += 1
                yield event
            else:
                # Heartbeat com mais informações
                heartbeat = {
                    "type": "heartbeat",
                    "message": "Mantendo conexão ativa",
                    "timestamp": datetime.utcnow().isoformat(),
                    "buffer_size": len(self._stream_buffer),
                    "last_index": last_index
                }
                print(f"Enviando heartbeat: {heartbeat}")
                yield heartbeat
                
                # Aguardar um pouco antes de verificar novamente
                import asyncio
                await asyncio.sleep(0.5)
    
    # ------------------------------------------
    # SELECIONAR FERRAMENTA AUTOMATICAMENTE
    # ------------------------------------------
    async def _select_tool(self, text: str):
        """
        Usa o LLM para identificar se há uma ferramenta adequada.
        Retorna a ferramenta ou None.
        """

        tools = ToolRegistry.all()
        tool_names = ", ".join(tools.keys())

        system_prompt = (
            "Você é um roteador de ferramentas. "
            "Sua tarefa é decidir se um texto necessita de alguma ferramenta disponível."
        )

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

        if tool_name in tools:
            return tools[tool_name]

        return None

    # ------------------------------------------
    # EXECUÇÃO DIRETA VIA LLM
    # ------------------------------------------
    async def _run_llm(self, text: str) -> str:
        response = await self.llm.ainvoke([
            {"role": "system", "content": "Execute a tarefa de forma concisa e prática."},
            {"role": "user", "content": text}
        ])

        return response.content.strip()
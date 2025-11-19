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
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

        # Buffer para streaming (WebSocket)
        self._stream_buffer = []  # lista de dicts enviados incrementalmente

    # ------------------------------------------
    # STREAMING PARA O WEBSOCKET
    # ------------------------------------------
    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generator: retorna eventos em tempo real.
        O AgentService chama isso.
        """
        last_index = 0
        while True:
            if last_index < len(self._stream_buffer):
                event = self._stream_buffer[last_index]
                last_index += 1
                yield event
            else:
                # aguarda async (evita busy loop)
                import asyncio
                await asyncio.sleep(0.1)

    def _push_stream(self, event: Dict[str, Any]):
        """Adiciona evento no buffer para o WebSocket."""
        self._stream_buffer.append(event)

    # ------------------------------------------
    # EXECUTAR UM ÚNICO PASSO
    # ------------------------------------------
    async def run_step(self, step: Step) -> Dict[str, Any]:
        """
        Executa um passo usando LLM + ferramentas.
        """

        self._push_stream({
            "type": "step_start",
            "step": step.order,
            "description": step.description
        })

        # Identificar qual ferramenta usar
        tool = await self._select_tool(step.description)

        # Executar ferramenta ou usar LLM direto
        if tool:
            result = await tool.execute(step.description)
        else:
            # Execução direto via modelo
            result = await self._run_llm(step.description)

        # Atualizar o banco de dados
        step.status = "completed"
        step.result = result
        step.updated_at = datetime.utcnow()
        self.db.commit()

        # Enviar evento ao WebSocket
        self._push_stream({
            "type": "step_complete",
            "step": step.order,
            "result": result
        })

        return result

    # ------------------------------------------
    # SELECIONAR FERRAMENTA AUTOMATICAMENTE
    # ------------------------------------------
    async def _select_tool(self, text: str):
        """
        Usa o LLM para identificar se há uma ferramenta adequada.
        Retorna a ferramenta ou None.
        """

        tools = ToolRegistry.list_tools()
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
from typing import Any, Dict, List
from datetime import datetime
from app.tools.base import BaseTool


class CalendarTool(BaseTool):
    """
    Ferramenta simulada de calendário.
    Permite criar, listar e cancelar eventos fictícios.
    """

    name = "calendar"
    description = "Gerencia eventos simples de calendário (simulado)."

    # Armazenamento simples em memória para simulação
    _events: List[Dict[str, Any]] = []

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        action: 'create', 'list', 'cancel'
        """

        if action == "create":
            return await self._create_event(kwargs)

        elif action == "list":
            return await self._list_events()

        elif action == "cancel":
            return await self._cancel_event(kwargs)

        return {"success": False, "error": f"Ação desconhecida: {action}"}

    async def _create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        title = data.get("title")
        date = data.get("date")

        if not title or not date:
            return {"success": False, "error": "Parâmetros 'title' e 'date' são obrigatórios"}

        try:
            dt = datetime.fromisoformat(date)
        except ValueError:
            return {"success": False, "error": "Formato de data inválido. Use ISO: yyyy-mm-dd HH:MM"}

        event = {
            "id": len(self._events) + 1,
            "title": title,
            "date": dt.isoformat()
        }

        self._events.append(event)

        return {"success": True, "event": event}

    async def _list_events(self) -> Dict[str, Any]:
        return {
            "success": True,
            "events": self._events
        }

    async def _cancel_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = data.get("id")

        if not event_id:
            return {"success": False, "error": "Parâmetro 'id' é obrigatório"}

        for e in self._events:
            if e["id"] == event_id:
                self._events.remove(e)
                return {"success": True, "message": f"Evento {event_id} cancelado"}

        return {"success": False, "error": f"Evento {event_id} não encontrado"}
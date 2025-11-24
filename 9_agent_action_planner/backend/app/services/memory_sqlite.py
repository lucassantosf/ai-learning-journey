from sqlalchemy.orm import Session
from typing import Any, List, Dict
from app.models.db_models import MemoryLog
import json


class SQLiteMemory:
    """
    Serviço simples de memória baseado em SQLite,
    usando o mesmo Session síncrono que o restante do sistema.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # Salvar logs
    # ---------------------------
    def add_log(self, log_type: str, content: Any):
        """
        Salva um log no formato:
        - type: string indicando o tipo (planner_output, step_result, etc)
        - content: JSON ou string
        """
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        log = MemoryLog(
            type=log_type,
            content=content
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    # ---------------------------
    # Recuperar logs
    # ---------------------------
    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        logs = (
            self.db.query(MemoryLog)
            .order_by(MemoryLog.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for log in logs:
            try:
                parsed = json.loads(log.content)
            except:
                parsed = log.content

            result.append({
                "id": log.id,
                "type": log.type,
                "content": parsed,
                "created_at": log.created_at.isoformat(),
            })

        return result
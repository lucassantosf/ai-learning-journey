from sqlalchemy.orm import Session
from typing import Any, List, Dict
from app.models.db_models import MemoryLog


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
    def add_log(self, user_message: str, ai_response: Any = None):
        log = MemoryLog(
            user_message=str(user_message),
            ai_response=str(ai_response)
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

        return [
            {
                "id": log.id,
                "user_message": log.user_message,
                "ai_response": log.ai_response,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
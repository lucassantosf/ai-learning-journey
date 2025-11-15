# backend/tests_playground/langgraph/01_memory_sqlite.py
import sqlite3
from datetime import datetime
from typing import List

class SQLiteMemory:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                timestamp TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_text TEXT,
                step_order INTEGER,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    def add(self, message: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO memory_logs (message, timestamp) VALUES (?, ?)",
                    (message, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def list(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, message, timestamp FROM memory_logs")
        rows = cur.fetchall()
        conn.close()
        return rows

    def clear(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM memory_logs")
        conn.commit()
        conn.close()

    def save_steps(self, steps: List[str]):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        for i, step in enumerate(steps, start=1):
            cur.execute(
                "INSERT INTO steps (step_text, step_order, timestamp) VALUES (?, ?, ?)",
                (step, i, datetime.now().isoformat())
            )

        conn.commit()
        conn.close()

    def list_steps(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, step_text, step_order, timestamp FROM steps ORDER BY step_order ASC")
        rows = cur.fetchall()
        conn.close()
        return rows

if __name__ == "__main__":
    from tests_playground.langgraph.planner_executor_basic_02 import SimplePlanner

    memory = SQLiteMemory()

    planner = SimplePlanner()
    plan = planner.plan("Planejar uma viagem de São Paulo a Salvador")

    print("Salvando etapas...")
    memory.save_steps(plan)

    print("\nListando etapas salvas:")
    for step in memory.list_steps():
        print(step)
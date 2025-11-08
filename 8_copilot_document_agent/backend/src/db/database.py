# src/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.logger import log_info

# ======================================================
# 📦 Configuração do Banco (SQLite)
# ======================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# Para SQLite, precisamos de um flag especial:
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Cria engine SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# ======================================================
# 🔧 Funções auxiliares
# ======================================================

def get_db():
    """Dependency (para FastAPI) que fornece uma sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria as tabelas no banco (se ainda não existirem)."""
    from src.db import models  # Importa modelos antes de criar
    log_info("🗄️ Inicializando banco de dados...")
    Base.metadata.create_all(bind=engine)
    log_info("✅ Banco de dados pronto!")
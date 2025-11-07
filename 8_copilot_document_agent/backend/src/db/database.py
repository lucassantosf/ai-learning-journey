# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# ======================================================
# 📦 Configuração do banco de dados
# ======================================================

# Define o URL do banco via variável de ambiente ou usa SQLite como fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# Configuração específica para SQLite (permite multithreading)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Cria a engine
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False, future=True)

# Cria a fábrica de sessões (SessionLocal será injetado nas rotas e repositórios)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos ORM
Base = declarative_base()

# ======================================================
# 🧩 Funções auxiliares
# ======================================================

def get_db():
    """
    Dependência para injeção no FastAPI:
    - Abre uma sessão de banco.
    - Fecha automaticamente após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    """
    Context manager útil fora do FastAPI (scripts, testes, etc.)
    Exemplo:
        with db_session() as db:
            db.add(obj)
            db.commit()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser chamada uma vez, no início da aplicação.
    """
    from src.db import models  # Import tardio para evitar import circular
    Base.metadata.create_all(bind=engine)
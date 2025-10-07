import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Caminho absoluto para o diretório backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Pasta data centralizada
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

# Caminho final do banco
DB_PATH = os.path.join(DB_DIR, "data.db")

# URL completa para o SQLite
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine e sessão
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necessário pro SQLite com FastAPI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
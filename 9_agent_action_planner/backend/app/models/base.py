from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Base para os modelos SQLAlchemy
Base = declarative_base()

# ---------------------------
# Engine + Session Local
# ---------------------------
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # necessário para SQLite
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ---------------------------
# Função usada nas rotas / dependências
# ---------------------------
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
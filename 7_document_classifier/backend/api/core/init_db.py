from api.core.database import Base, engine
from api.core import models                 

def init_db():
    print("🔧 Criando tabelas no banco...")
    Base.metadata.create_all(bind=engine)
    print("✅ Banco inicializado com sucesso.")

if __name__ == "__main__":
    init_db()

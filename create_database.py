import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base
import datetime

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "app_users"
    __table_args__ = {"schema": "core"}
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    sobrenome = Column(String(100), nullable=False )
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    cpf = Column(String(255), unique = True, nullable = False)
    telefone = Column(String(255), unique = True, nullable = False)
    risk_profile = Column(String(50), default="MODERADO")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

if __name__ == "__main__":
    print("Conectando ao banco...")

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS core;"))
        conn.commit()

    print("Criando tabela no schema 'core'...")
    Base.metadata.create_all(bind=engine)
    
    print("Tabela 'core.app_users' criada com sucesso!")
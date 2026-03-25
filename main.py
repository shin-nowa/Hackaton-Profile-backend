import os
import create_database
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, EmailStr
import datetime

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "app_users"
    __table_args__ = {"schema": "core"}
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    sobrenome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    telefone = Column(String(20))
    risk_profile = Column(String(50), default="MODERADO")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS core;"))
    conn.commit()
    Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    nome: str
    sobrenome: str
    email: EmailStr
    password_hash: str
    cpf: str
    telefone: str
    risk_profile: str = "MODERADO"

class UserUpdate(BaseModel):
    nome: str | None = None
    sobrenome: str | None = None
    telefone: str | None = None
    risk_profile: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == user.email) | (User.cpf == user.cpf)).first():
        raise HTTPException(status_code=400, detail="Email ou CPF já cadastrado.")

    new_user = User(
        nome=user.nome,
        sobrenome=user.sobrenome,
        email=user.email,
        password_hash=user.password_hash,
        cpf=user.cpf,
        telefone=user.telefone,
        risk_profile=user.risk_profile.upper()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_dict = updated_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}
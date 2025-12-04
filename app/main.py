from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI(title="User Management API")

# --- Подключение к БД ---
DB_USER = os.getenv("DB_USER", "default_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_password")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Это будет 'postgres-service' в Kubernetes
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "default_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()


# --- Определение модели ---
class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)


Base.metadata.create_all(bind=engine)


# --- Pydantic модели для API ---
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


def get_db():
    """Зависимость для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users_from_db(skip: int = 0, limit: int = 100):
    db = next(get_db())
    users = db.query(UserORM).offset(skip).limit(limit).all()
    return users


def create_user_in_db(user: UserCreate):
    db = next(get_db())
    db_user = UserORM(username=user.username, email=user.email)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")
    return db_user


@app.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100):
    users = get_users_from_db(skip=skip, limit=limit)
    return users


@app.post("/users", response_model=UserResponse)
def add_user(user: UserCreate):
    db_user = create_user_in_db(user)
    return db_user


@app.get("/health")
def health_check():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "details": str(e)}
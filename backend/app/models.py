from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Base(DeclarativeBase):
    pass


class UserDB(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    is_active: bool = Column(Boolean, default=True)
    is_superuser: bool = Column(Boolean, default=False)
    department: str | None = Column(String(100), nullable=True)  # дополнительно для предприятия

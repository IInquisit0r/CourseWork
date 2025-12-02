import uuid
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from models import UserDB
from database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserDB)


# UserManager implementation
class UserManager(UUIDIDMixin, BaseUserManager[UserDB, uuid.UUID]):
    reset_password_token_secret = "SECRET-RESET-PASSWORD"
    verification_token_secret = "SECRET-VERIFY-EMAIL"

    async def on_after_register(self, user: UserDB, request=None):
        print(f"User {user.id} registered")


# Dependency for FastAPI Users
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

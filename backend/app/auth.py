import uuid
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy

from models import UserDB
from user_manager import get_user_manager


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret="SUPER-SECRET-KEY-CHANGE-ME",
        lifetime_seconds=3600 * 24 * 30
    )


fastapi_users = FastAPIUsers[UserDB, uuid.UUID](
    get_user_manager,
    [get_jwt_strategy()]
)

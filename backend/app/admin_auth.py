from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from auth import get_jwt_strategy
from user_manager import get_user_manager
from fastapi import Depends


class AdminAuth(AuthenticationBackend):

    async def login(
            self,
            request: Request,
            user_manager=Depends(get_user_manager)
    ) -> bool:
        form = await request.form()
        token = form.get("token")

        jwt = get_jwt_strategy()

        try:
            payload = await jwt.read_token(token, user_manager)
            request.session.update({"token": token})
            return True
        except Exception:
            return False

    async def authenticate(
            self,
            request: Request,
            user_manager=Depends(get_user_manager)
    ):
        token = request.session.get("token")
        if not token:
            return None

        jwt = get_jwt_strategy()

        try:
            payload = await jwt.read_token(token, user_manager)
        except Exception:
            return None

        return True

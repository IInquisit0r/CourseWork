from sqladmin import Admin, ModelView
from main import app
import models
import database
from admin_auth import AdminAuth


class UserAdmin(ModelView, model=models.UserDB):
    column_list = [
        models.UserDB.id,
        models.UserDB.email,
        models.UserDB.is_active,
        models.UserDB.department
    ]
    form_columns = [
        models.UserDB.email,
        models.UserDB.department,
        models.UserDB.is_active
    ]


admin = Admin(
    app=app,
    engine=database.engine,
    authentication_backend=AdminAuth(secret_key="SUPER_ADMIN_SECRET")
)

admin.add_view(UserAdmin)

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="User Management API")

users = []


class User(BaseModel):
    username: str
    email: str


@app.get("/users")
def get_users():
    return users


@app.post("/users")
def add_user(user: User):
    users.append(user.dict())
    return {"message": "User added successfully", "user": user}
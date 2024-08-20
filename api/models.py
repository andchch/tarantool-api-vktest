from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    hashed_password: str

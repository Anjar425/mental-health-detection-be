from pydantic import BaseModel
from typing import Optional
from app.models.user import RoleEnum
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.user
class UserLogin(BaseModel):
    email: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    email: Optional[str] = None

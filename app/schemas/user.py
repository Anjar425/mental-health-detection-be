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
    role: Optional[RoleEnum] = None
    username: Optional[str] = None
    id: Optional[int] = None

class TokenData(BaseModel):
    email: Optional[str] = None


from typing import List

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    groups: Optional[List[str]] = None  # List of group names for debugging/response

    class Config:
        orm_mode = True

class MeResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    redirect_to: str

    class Config:
        orm_mode = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    id: int
    username: str
    email: str
    role: str
    redirect_to: str

    class Config:
        orm_mode = True

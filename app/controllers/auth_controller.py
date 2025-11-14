from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from ..config import settings
from sqlalchemy.orm import Session

from .base_controller import BaseController

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthController(BaseController):
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        # Potong password jika panjangnya lebih dari 72 byte
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def authenticate_user(self, db: Session, email: str, password: str):
        user = self.get_user(db, email=email)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

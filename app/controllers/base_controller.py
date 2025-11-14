from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from ..database import get_db
from ..models import User
from ..schemas import TokenData
from ..config import settings 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class BaseController:
    def get_session(self):
        return get_db()
    
    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),  
        db: Session = Depends(get_db)
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode token dengan secret_key dan algoritma yang diset di settings
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email: str = payload.get("sub")  # 'sub' adalah claim standar yang digunakan untuk user identifier

            if email is None:
                raise credentials_exception
            
            # Membuat object TokenData dengan email yang didapat dari token
            token_data = TokenData(email=email)
        
        except JWTError:
            raise credentials_exception

        # Query user berdasarkan email dari token
        user = self.get_user(db, email=token_data.email)

        # Jika user tidak ditemukan, lempar exception
        if user is None:
            raise credentials_exception

        return user
    
    def get_user(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

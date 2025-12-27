from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, RoleEnum
from ..schemas import UserCreate, UserLogin, AuthResponse, MeResponse
from ..config import settings

from ..controllers import AuthController
from ..schemas import UserResponse

router = APIRouter()
auth = AuthController()

@router.post("/register", response_model=AuthResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    
    # Enforce public registrations to always be regular users (no admin)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role=RoleEnum.user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": db_user.email, "role": db_user.role.value, "username": db_user.username, "id": db_user.id}, expires_delta=access_token_expires
    )
    
    redirect = "/admin/dashboard" if db_user.role == RoleEnum.admin else "/user/dashboard"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role.value,
        "redirect_to": redirect,
    }

@router.post("/login", response_model=AuthResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    # Ambil role dari database, bukan dari request user
    access_token = auth.create_access_token(
        data={
            "sub": db_user.email,
            "id": db_user.id,
            "role": db_user.role.value,
            "username": db_user.username
        },
        expires_delta=access_token_expires
    )

    # Return user info so frontend can redirect properly
    redirect = "/admin/dashboard" if db_user.role == RoleEnum.admin else "/user/dashboard"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role.value,
        "redirect_to": redirect,
    }


@router.get("/me", response_model=MeResponse)
def read_current_user(current_user=Depends(auth.get_current_user)):
    # Return current authenticated user info with redirect target
    redirect = "/admin/dashboard" if current_user.role == RoleEnum.admin else "/user/dashboard"
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "redirect_to": redirect,
    }


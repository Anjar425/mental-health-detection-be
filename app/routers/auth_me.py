from fastapi import APIRouter, Depends
from ..controllers import AuthController
from ..schemas import UserResponse

router = APIRouter()
auth = AuthController()

@router.get('/me', response_model=UserResponse)
def me(current_user=Depends(auth.get_current_user)):
    return current_user

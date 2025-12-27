from fastapi import Depends, HTTPException, status
from ..controllers.base_controller import BaseController
from ..models.user import RoleEnum
from ..models import User

base_ctrl = BaseController()

def require_admin(current_user: User = Depends(BaseController().get_current_user)):
    if current_user is None or current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def require_admin_or_expert(current_user: User = Depends(BaseController().get_current_user)):
    if current_user is None or current_user.role not in (RoleEnum.admin, RoleEnum.expert):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or expert privileges required")
    return current_user


def require_authenticated_user(current_user: User = Depends(BaseController().get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..controllers.permissions import require_admin
from ..models import User, RoleEnum
from ..schemas import UserResponse
from ..controllers.decission_support_system_controller import DecissionSupportSystemController
from ..schemas.decission_support_system import ExpertRankingOut, ConsensusItem

router = APIRouter()

dss_ctrl = DecissionSupportSystemController()

from fastapi import Query

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    q: str = Query(None),
    sort: str = Query(None),
    order: str = Query("asc")
):
    query = db.query(User)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    total = query.count()
    if sort and hasattr(User, sort):
        col = getattr(User, sort)
        if order == "desc":
            col = col.desc()
        query = query.order_by(col)
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": users,
        "total": total,
        "page": page,
        "perPage": per_page
    }

@router.get("/experts")
def get_all_experts(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    q: str = Query(None),
    sort: str = Query(None),
    order: str = Query("asc")
):
    query = db.query(User).filter(User.role == RoleEnum.expert)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    total = query.count()
    if sort and hasattr(User, sort):
        col = getattr(User, sort)
        if order == "desc":
            col = col.desc()
        query = query.order_by(col)
    experts = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": experts,
        "total": total,
        "page": page,
        "perPage": per_page
    }

@router.get("/rankings", response_model=list[ExpertRankingOut])
def get_expert_rankings(current_user=Depends(require_admin)):
    rankings = dss_ctrl.get_expert_rankings()
    return rankings

@router.get("/consensus", response_model=list[ConsensusItem])
def get_consensus_model(current_user=Depends(require_admin)):
    consensus = dss_ctrl.get_consensus_model()
    return consensus

from typing import List

from fastapi import APIRouter, Depends

from app.controllers.expert_group_controller import ExpertGroupController
from app.controllers.permissions import require_admin_or_expert
from app.models.user import RoleEnum, User
from app.schemas.expert_group import ExpertGroupSummary
from app.schemas.group_ranking import GroupRankingResponse

router = APIRouter()


@router.get("", response_model=List[ExpertGroupSummary])
def list_my_groups(current_user: User = Depends(require_admin_or_expert)) -> List[ExpertGroupSummary]:
    controller = ExpertGroupController()
    if current_user.role == RoleEnum.admin:
        return controller.get_all_groups()
    return controller.get_groups_for_user(current_user.id)


@router.get("/{group_id}/rankings", response_model=GroupRankingResponse)
def get_group_rankings_for_member(
    group_id: int,
    current_user: User = Depends(require_admin_or_expert),
) -> GroupRankingResponse:
    controller = ExpertGroupController()
    if current_user.role == RoleEnum.admin:
        return controller.get_group_rankings(group_id)
    return controller.get_group_rankings_for_expert(group_id, current_user.id)

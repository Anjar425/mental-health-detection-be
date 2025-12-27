from typing import List

from fastapi import APIRouter, Depends

from app.controllers.expert_group_controller import ExpertGroupController
from app.controllers.permissions import require_authenticated_user
from app.schemas.expert_group import ExpertGroupSummary

router = APIRouter()


@router.get("", response_model=List[ExpertGroupSummary])
def list_groups_for_authenticated_user(
    current_user=Depends(require_authenticated_user),
) -> List[ExpertGroupSummary]:
    controller = ExpertGroupController()
    return controller.get_all_groups()

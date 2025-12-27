
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.expert_group import ExpertGroupCreate, ExpertGroupUpdate, ExpertGroupOut, ExpertGroupSummary
from app.schemas.group_ranking import GroupRankingResponse
from app.controllers.expert_group_controller import ExpertGroupController
from app.controllers.permissions import require_admin
from typing import List
from app.schemas.user import UserResponse
router = APIRouter()


# GET / - List all groups with member_count
@router.get("", response_model=List[ExpertGroupSummary])
def list_groups(current_user=Depends(ExpertGroupController().get_current_user)):
    try:
        return ExpertGroupController().get_all_groups()
    except Exception as exc:
        import logging
        logging.exception("Failed to list expert groups")
        raise HTTPException(status_code=500, detail=f"Failed to list groups: {str(exc)}")

 # GET /{id} - Get group details with members
@router.get("/{group_id}", response_model=ExpertGroupOut, dependencies=[Depends(require_admin)])
def get_group(group_id: int):
    group = ExpertGroupController().get_group_with_members(group_id)
    # Convert to schema with members
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return ExpertGroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=str(group.created_at) if group.created_at else None,
        members=[UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            groups=[g.name for g in u.groups] if u.groups else []
        ) for u in group.experts]
    )

 # POST / - Create group
@router.post("", response_model=ExpertGroupOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_group(data: ExpertGroupCreate):
    group = ExpertGroupController().create_group(data=data)
    return ExpertGroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=str(group.created_at) if group.created_at else None
    )

# POST /groups/{id}/members (add single member by user_id in body)
from pydantic import BaseModel
class AddMemberRequest(BaseModel):
    user_id: int

@router.post("/{group_id}/members", response_model=ExpertGroupOut, dependencies=[Depends(require_admin)])
def add_member(group_id: int, req: AddMemberRequest):
    group = ExpertGroupController().add_expert_to_group(group_id, req.user_id)
    return ExpertGroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=str(group.created_at) if group.created_at else None
    )

@router.post("/{group_id}/invalidate-cache", dependencies=[Depends(require_admin)])
def invalidate_cache(group_id: int):
    controller = ExpertGroupController()
    res = controller.invalidate_group_weights(group_id)
    return res

@router.post("/{group_id}/recompute-weights", dependencies=[Depends(require_admin)])
def recompute_weights(group_id: int):
    controller = ExpertGroupController()
    res = controller.recompute_group_weights(group_id)
    return res

@router.get("/{group_id}/signature-info", dependencies=[Depends(require_admin)])
def get_group_signature_info(group_id: int):
    controller = ExpertGroupController()
    return controller.get_group_signature_info(group_id)

 # PUT /{id} - Update group
@router.put("/{group_id}", response_model=ExpertGroupOut, dependencies=[Depends(require_admin)])
def update_group(group_id: int, data: ExpertGroupUpdate):
    group = ExpertGroupController().update_group(group_id, data)
    return ExpertGroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=str(group.created_at) if group.created_at else None
    )


@router.get("/{group_id}/rankings", response_model=GroupRankingResponse, dependencies=[Depends(require_admin)])
def get_group_rankings(group_id: int):
    return ExpertGroupController().get_group_rankings(group_id)

 # DELETE /{group_id} - Delete group
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_group(group_id: int):
    ExpertGroupController().delete_group(group_id)
    return None

 # POST /{groupId}/members - Add expert to group (with body)
@router.post("/{group_id}/members", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
def add_expert_body(group_id: int, req: AddMemberRequest):
    group = ExpertGroupController().add_expert_to_group(group_id, req.user_id)
    return group

 # POST /{groupId}/members/{expertId} - Add expert to group
@router.post("/{group_id}/members/{expert_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
def add_expert(group_id: int, expert_id: int):
    group = ExpertGroupController().add_expert_to_group(group_id, expert_id)
    return group

 # DELETE /{group_id}/members/{expert_id} - Remove expert from group
@router.delete("/{group_id}/members/{expert_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
def remove_expert(group_id: int, expert_id: int):
    group = ExpertGroupController().remove_expert_from_group(group_id, expert_id)
    return group

from typing import List

from fastapi import APIRouter, Depends

from app.controllers.expert_group_controller import ExpertGroupController
from app.controllers.permissions import require_authenticated_user
from app.schemas.expert_group import ExpertGroupSummary
from app.schemas.group_public_summary import GroupPublicSummary

router = APIRouter()


@router.get("", response_model=List[ExpertGroupSummary])
def list_groups_for_authenticated_user(
    current_user=Depends(require_authenticated_user),
) -> List[ExpertGroupSummary]:
    controller = ExpertGroupController()
    return controller.get_all_groups()


@router.get("/{group_id}/summary", response_model=GroupPublicSummary)
def get_group_public_summary(
    group_id: int,
    current_user=Depends(require_authenticated_user),
) -> GroupPublicSummary:
    """
    Public anonymized summary for a group, visible to any authenticated user.
    Computes stats from group rankings without exposing identities.
    """
    controller = ExpertGroupController()
    # Internally reuse ranking computation, but return anonymized aggregates
    ranking = controller.get_group_rankings(group_id)

    s3_count = 0
    s2_count = 0
    max_experience_years = 0
    total_patients = 0
    max_publication = 0

    for r in ranking.rankings:
        level = (r.capability.education_level or "").upper()
        if "S3" in level or "DOKTOR" in level:
            s3_count += 1
        elif "S2" in level or "MAGISTER" in level:
            s2_count += 1
        years = int(r.capability.flight_hours or 0)
        if years > max_experience_years:
            max_experience_years = years
        total_patients += int(r.capability.patient_count or 0)
        pubs = int(r.capability.publication_count or 0)
        if pubs > max_publication:
            max_publication = pubs

    member_count = len(ranking.rankings)
    avg_patients = int(round(total_patients / member_count)) if member_count > 0 else 0

    return GroupPublicSummary(
        group_id=ranking.group_id,
        group_name=ranking.group_name,
        description=ranking.description,
        member_count=member_count,
        s3_count=s3_count,
        s2_count=s2_count,
        max_experience_years=max_experience_years,
        avg_patient_per_year=avg_patients,
        max_publication_count=max_publication,
    )

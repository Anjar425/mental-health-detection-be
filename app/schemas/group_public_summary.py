from pydantic import BaseModel
from typing import Optional


class GroupPublicSummary(BaseModel):
    group_id: int
    group_name: str
    description: Optional[str] = None
    member_count: int
    s3_count: int
    s2_count: int
    max_experience_years: int
    avg_patient_per_year: int
    max_publication_count: int

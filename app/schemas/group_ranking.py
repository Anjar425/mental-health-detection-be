from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional


class ExpertCapabilityOut(BaseModel):
    education_level: Optional[str] = None
    publication_count: int
    patient_count: int
    flight_hours: int
    weight_JT: float
    weight_Pat: float
    weight_Pend: float
    weight_Pub: float


class ExpertPreferenceOut(BaseModel):
    question_id: int
    depression: float
    anxiety: float
    stress: float


class GroupExpertRankingOut(BaseModel):
    user_id: int
    username: str
    email: str
    influence_score: float
    influence_percent: float
    capability: ExpertCapabilityOut
    preferences: List[ExpertPreferenceOut]
    rank: int


class GroupConsensusOut(BaseModel):
    question_id: int
    depression: float
    anxiety: float
    stress: float


class WeightInfo(BaseModel):
    signature: Optional[str] = None
    created_at: Optional[str] = None
    meta: Optional[dict] = None
    weights_by_user: Optional[List[dict]] = None


class GroupRankingResponse(BaseModel):
    group_id: int
    group_name: str
    description: Optional[str] = None
    rankings: List[GroupExpertRankingOut]
    consensus_matrix: List[GroupConsensusOut]
    weights_info: Optional[WeightInfo] = None

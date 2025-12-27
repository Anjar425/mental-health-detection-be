from pydantic import BaseModel
from typing import List, Optional

class PreferenceItem(BaseModel):
    D: float
    A: float
    S: float

class ExpertCapabilityIn(BaseModel):
    expert_id: str 
    JamTerbang: int 
    Patients: int 
    Pendidikan: int 
    Publikasi: int 

    weight_JamTerbang: float
    weight_Patients: float 
    weight_Pendidikan: float 
    weight_Publikasi: float 

class ExpertPreferencesOut(BaseModel):
    expert_id: str
    preferences: List[PreferenceItem]

class PatientScoreIn(BaseModel):
    scores: List[int]
    type: str = "21"
    group_id: Optional[int] = None

class ExpertRankingOut(BaseModel):
    expert_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    weight: float
    rank: int

class ConsensusItem(BaseModel):
    dass21_id: int
    depression: float
    anxiety: float
    stress: float

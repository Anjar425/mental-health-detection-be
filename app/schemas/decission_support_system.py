from pydantic import BaseModel
from typing import List

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
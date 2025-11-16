from pydantic import BaseModel
from typing import Optional

class ExpertProfileBase(BaseModel):
    education_level: Optional[str] = None
    publication_count: Optional[int] = None
    patient_count: Optional[int] = None
    flight_hours: Optional[int] = None

class ExpertWeightBase(BaseModel):
    education_weight: Optional[int] = None
    publication_weight: Optional[int] = None
    patient_weight: Optional[int] = None
    flight_hours_weight: Optional[int] = None

class ExpertWeightCreate(ExpertWeightBase):
    pass

class ExpertWeightResponse():
    id: int
    user_id: int
    weight: ExpertWeightBase

class ExpertProfileResponse(BaseModel):
    profile: ExpertProfileBase
    weight: ExpertWeightBase

class ExpertProfileCreate(ExpertProfileResponse):
    pass
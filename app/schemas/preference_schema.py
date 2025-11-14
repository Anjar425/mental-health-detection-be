from pydantic import BaseModel
from typing import Optional

class PreferenceBase(BaseModel):
    user_id: int
    dass21_id: int
    percent_anxiety: Optional[int] = None
    percent_depression: Optional[int] = None
    percent_stress: Optional[int] = None

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int

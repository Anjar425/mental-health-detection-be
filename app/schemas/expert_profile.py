from pydantic import BaseModel
from typing import Optional

class ExpertProfileBase(BaseModel):
    education_level: Optional[str] = None
    publication_count: Optional[int] = None
    patient_count: Optional[int] = None
    flight_hours: Optional[int] = None

class ExpertProfileCreate(ExpertProfileBase):
    pass

class ExpertProfileResponse(ExpertProfileBase):
    id: int
    user_id: int
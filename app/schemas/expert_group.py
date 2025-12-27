from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class ExpertGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

from pydantic import field_validator
from typing import List

class ExpertGroupCreate(ExpertGroupBase):
    expert_ids: List[int]

    @field_validator("expert_ids")
    @classmethod
    def at_least_two_experts(cls, v):
        if not v or len(v) < 2:
            raise ValueError("At least 2 experts are required to create a group.")
        return v

class ExpertGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ExpertGroupOut(ExpertGroupBase):
    id: int
    created_at: Optional[str] = None
    members: Optional[List["UserOut"]] = None
    model_config = ConfigDict(from_attributes=True)

from app.schemas.user import UserResponse as UserOut
ExpertGroupOut.model_rebuild()

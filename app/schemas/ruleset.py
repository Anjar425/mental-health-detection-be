from pydantic import BaseModel
from typing import List, Optional


class PremiseResponse(BaseModel):
    id: int
    dass42_id: int
    rule_id: int
    prefix: str
    level: str
    conjunction: str

    class Config:
        from_attributes = True


class ConclusionResponse(BaseModel):
    id: int
    category_id: int
    severity_id: int

    class Config:
        from_attributes = True


class RuleResponse(BaseModel):
    id: int
    user_id: Optional[int]
    conclusion_id: int
    conclusion: Optional[ConclusionResponse]
    premises: List[PremiseResponse]

    class Config:
        from_attributes = True


class PremiseSchema(BaseModel):
    dass42_id: Optional[int]
    prefix: Optional[str]
    level: Optional[str]
    conjunction: Optional[str]


class ConclusionSchema(BaseModel):
    category: Optional[str]
    severity: Optional[str]


class RulesContentSchema(BaseModel):
    premises: List[PremiseSchema]
    conclusion: ConclusionSchema


class RuleResponseSchema(BaseModel):
    rule_id: int
    rules: RulesContentSchema

class RuleCreateOrUpdate(RulesContentSchema):
    rule_id: Optional[int]
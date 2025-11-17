from pydantic import BaseModel
from typing import Dict, Optional


class FuzzyInferenceRequest(BaseModel):
    """
    Request body for fuzzy inference computation.
    
    Attributes:
        questionnaire_responses: Dictionary mapping Q1..Q42 to values (0-3)
        category: Optional category filter ("depression", "anxiety", "stress")
                 If omitted, all categories will be computed
    """
    questionnaire_responses: Dict[str, int]
    category: Optional[str] = None

    class Config:
        example = {
            "questionnaire_responses": {
                "Q1": 0,
                "Q2": 1,
                "Q3": 2,
                "Q4": 3,
                # ... Q5 through Q42
            },
            "category": "depression"  # optional
        }


class MembershipDegreesResponse(BaseModel):
    """Membership degrees for each fuzzy output class."""
    Normal: float
    Mild: float
    Moderate: float
    Severe: float
    Extremely_Severe: float

    class Config:
        from_attributes = True


class FuzzyInferenceResponse(BaseModel):
    """
    Response for a single fuzzy inference result.
    
    Attributes:
        category: The category name ("depression", "anxiety", or "stress")
        score: Defuzzified output score
        membership_degrees: Dictionary of fuzzy labels and their membership values
    """
    category: str
    score: Optional[float]
    membership_degrees: Dict[str, float]

    class Config:
        from_attributes = True


class FuzzyInferenceAllResponse(BaseModel):
    """
    Response containing fuzzy inference results for all categories.
    """
    depression: FuzzyInferenceResponse
    anxiety: FuzzyInferenceResponse
    stress: FuzzyInferenceResponse

    class Config:
        from_attributes = True

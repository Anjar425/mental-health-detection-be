from fastapi import APIRouter, Depends
from ..schemas import ExpertProfileCreate, ExpertProfileResponse, PatientScoreIn
from ..controllers import DecissionSupportSystemController

router = APIRouter()

@router.post("/")
def calculate_qdds(payload: PatientScoreIn):
    scores = payload.scores
    return DecissionSupportSystemController().calculate_qdds(data=scores)

from fastapi import APIRouter, Depends
from ..schemas import ExpertProfileCreate, ExpertProfileResponse
from ..controllers import ExpertProfilesController

router = APIRouter()

@router.get("/", response_model=ExpertProfileResponse)
def get_my_profile(current_user=Depends(ExpertProfilesController().get_current_user)):
    return ExpertProfilesController().get_my_profile(current_user=current_user)

@router.post("/", response_model=ExpertProfileCreate)
def create_or_update_profile(data: ExpertProfileCreate, current_user=Depends(ExpertProfilesController().get_current_user)):
    return ExpertProfilesController().create_or_update_profile(data=data, current_user=current_user)
    
@router.get("/get-all")
def get_all():
    return ExpertProfilesController().get_all_profiles()

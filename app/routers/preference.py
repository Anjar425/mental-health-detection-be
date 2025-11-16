from fastapi import APIRouter, Depends
from ..schemas import PreferenceCreate
from ..controllers import PreferencesController

router = APIRouter()

@router.get("/")
def get_my_preference(current_user=Depends(PreferencesController().get_current_user)):
    return PreferencesController().get_my_preference(current_user=current_user)

@router.post("/")
def get_my_preference(data: PreferenceCreate, current_user=Depends(PreferencesController().get_current_user)):
    return PreferencesController().create_or_update_preference(data=data, current_user=current_user)

@router.get("/get-all")
def get_all():
    return PreferencesController().get_all_preference()
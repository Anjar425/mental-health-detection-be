from fastapi import APIRouter, Depends
from ..schemas import ExpertProfileCreate, ExpertProfileResponse, PatientScoreIn
from ..controllers import DecissionSupportSystemController

router = APIRouter()


@router.post("/")
def calculate_qdds(payload: PatientScoreIn, current_user=Depends(DecissionSupportSystemController().get_current_user)):
    controller = DecissionSupportSystemController()
    return controller.calculate_qdds(data=payload.scores, current_user=current_user, assessment_type=payload.type)

@router.post("/public")
def calculate_public_qdds(payload: PatientScoreIn):
    """
    Endpoint khusus Guest (Tanpa Login).
    Hanya menghitung skor, TIDAK menyimpan ke database.
    """
    controller = DecissionSupportSystemController()
    
    # Perhatikan: current_user kita isi None
    # Controller akan otomatis tau jika user None = Jangan simpan ke DB
    return controller.calculate_qdds(
        data=payload.scores, 
        current_user=None, 
        assessment_type=payload.type
    )


@router.get("/history")
def get_user_history(current_user=Depends(DecissionSupportSystemController().get_current_user)):
    """
    Retrieve the logged-in user's assessment history.
    Returns records ordered by newest first.
    """
    return DecissionSupportSystemController().get_user_history(current_user=current_user)


@router.delete("/history/{history_id}")
def delete_user_history(history_id: int, current_user=Depends(DecissionSupportSystemController().get_current_user)):
    """
    Delete a specific assessment history record for the logged-in user.
    Returns 404 if record not found, 403 if not owned by user.
    """
    return DecissionSupportSystemController().delete_history(history_id=history_id, current_user=current_user)
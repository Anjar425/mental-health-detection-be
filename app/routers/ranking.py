from fastapi import APIRouter, Depends
from ..controllers import RankingController
from ..controllers import BaseController

router = APIRouter()

@router.get("/")
def get_rankings():
    """
    Mendapatkan skor ranking SAW khusus untuk user yang sedang login.
    Nilai tetap dihitung berdasarkan normalisasi global (dibandingkan dengan pakar lain),
    tetapi output hanya menampilkan data user tersebut.
    """
    controller = RankingController()
    return controller.get_expert_rankings()
@router.get("/me")
def get_my_ranking(current_user=Depends(RankingController().get_current_user)):
    """
    Mendapatkan ranking pakar untuk pengguna saat ini berdasarkan metode SAW.
    Data dinormalisasi dan dikalikan dengan rata-rata bobot seluruh pakar.
    """
    controller = RankingController()
    return controller.get_my_expert_rankings(current_user=current_user)
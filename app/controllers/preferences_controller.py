from .base_controller import BaseController
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Preference
from ..schemas import PreferenceCreate

class PreferencesController(BaseController):
    def get_all_preference(self):
        db: Session = next(self.get_session())

        rows = db.query(Preference).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Preference not found")

        result = {}

        for row in rows:
            uid = row.user_id

            if uid not in result:
                result[uid] = {
                    "user_id": uid,
                    "preferences": []
                }

            result[uid]["preferences"].append({
                "dass21_id": row.dass21_id,
                "percent_depression": row.percent_depression,
                "percent_anxiety": row.percent_anxiety,
                "percent_stress": row.percent_stress
            })

        # convert dict → list
        return list(result.values())
    
    def get_my_preference(self, current_user):
        db: Session = next(self.get_session())

        # Ambil preferences yang hanya milik current_user
        rows = db.query(Preference).filter(Preference.user_id == current_user.id).all()
        # if not rows:
        #     raise HTTPException(status_code=404, detail="Preferences not found for this user")

        # Proses hasil menjadi struktur yang diinginkan
        result = {
            "user_id": current_user.id,
            "preferences": []
        }

        for row in rows:
            result["preferences"].append({
                "dass21_id": row.dass21_id,
                "percent_depression": row.percent_depression,
                "percent_anxiety": row.percent_anxiety,
                "percent_stress": row.percent_stress
            })

        return result

    def create_or_update_preference(self, data: PreferenceCreate, current_user):
        db: Session = next(self.get_session())

        existing = (
            db.query(Preference)
            .filter(
                Preference.user_id == current_user.id,
                Preference.dass21_id == data.dass21_id
            )
            .first()
        )

        if existing:
            for key, value in data.dict().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing

        new_pref = Preference(
            user_id=current_user.id,
            **data.dict()
        )
        db.add(new_pref)
        db.commit()
        db.refresh(new_pref)
        return new_pref

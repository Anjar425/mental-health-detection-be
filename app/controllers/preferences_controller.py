from .base_controller import BaseController
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Preference
from ..schemas import PreferenceCreate

class PreferencesController(BaseController):
    def get_all_preference(self):
        db: Session = next(self.get_session())

        profile = db.query(Preference).all()
        if not profile:
            raise HTTPException(status_code=404, detail="Preference not found")

        return profile
    
    def get_my_preference(self, current_user):
        db: Session = next(self.get_session())
        preference = db.query(Preference).filter(Preference.user_id == current_user.id).first()
        if not preference:
            raise HTTPException(status_code=404, detail="Preference not found")

        return preference

    def create_or_update_preference(self, data: PreferenceCreate, current_user):
        db: Session = next(self.get_session())

        existing = db.query(Preference).filter(Preference.user_id == current_user.id).first()

        if existing:
            # Update profile
            for key, value in data.dict().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new profile
            new_profile = Preference(user_id=current_user.id, **data.dict())
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
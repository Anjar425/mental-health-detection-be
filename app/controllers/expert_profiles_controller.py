from .base_controller import BaseController
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import ExpertProfile
from ..schemas import ExpertProfileCreate

class ExpertProfilesController(BaseController):
    def get_all_profiles(self):
        db: Session = next(self.get_session())

        profile = db.query(ExpertProfile).all()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return profile
    
    def get_my_profile(self, current_user):
        db: Session = next(self.get_session())
        profile = db.query(ExpertProfile).filter(ExpertProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return profile

    def create_or_update_profile(self, data: ExpertProfileCreate, current_user):
        db: Session = next(self.get_session())

        existing = db.query(ExpertProfile).filter(ExpertProfile.user_id == current_user.id).first()

        if existing:
            # Update profile
            for key, value in data.dict().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new profile
            new_profile = ExpertProfile(user_id=current_user.id, **data.dict())
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
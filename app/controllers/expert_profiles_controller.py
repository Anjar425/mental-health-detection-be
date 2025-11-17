from .base_controller import BaseController
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import ExpertProfile, ExpertWeight
from ..schemas import ExpertProfileCreate

class ExpertProfilesController(BaseController):
    def get_all_profiles(self):
        db: Session = next(self.get_session())

        # Ambil semua profile
        profiles = db.query(ExpertProfile).all()

        # if not profiles:
        #     raise HTTPException(status_code=404, detail="No profiles found")

        results = []

        for profile in profiles:
            # Cari weight yang sesuai dengan user_id
            weight = db.query(ExpertWeight).filter(
                ExpertWeight.user_id == profile.user_id
            ).first()

            results.append({
                "id": profile.id,
                "user_id": profile.user_id,
                "profile": {
                    "education_level": profile.education_level,
                    "publication_count": profile.publication_count,
                    "patient_count": profile.patient_count,
                    "flight_hours": profile.flight_hours,
                },
                "weight": {
                    "education_weight": weight.education_weight if weight else None,
                    "publication_weight": weight.publication_weight if weight else None,
                    "patient_weight": weight.patient_weight if weight else None,
                    "flight_hours_weight": weight.flight_hours_weight if weight else None
                }
            })

        return results
    
    def get_my_profile(self, current_user):
        db: Session = next(self.get_session())

        profile = db.query(ExpertProfile).filter(
            ExpertProfile.user_id == current_user.id
        ).first()

        weight = db.query(ExpertWeight).filter(
            ExpertWeight.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "profile": {
                "education_level": profile.education_level,
                "publication_count": profile.publication_count,
                "patient_count": profile.patient_count,
                "flight_hours": profile.flight_hours,
            },
            "weight": {
                "education_weight": weight.education_weight if weight else None,
                "publication_weight": weight.publication_weight if weight else None,
                "patient_weight": weight.patient_weight if weight else None,
                "flight_hours_weight": weight.flight_hours_weight if weight else None
            }
        }

    def create_or_update_profile(self, data: ExpertProfileCreate, current_user):
        db: Session = next(self.get_session())

        existing_profile = db.query(ExpertProfile).filter(
            ExpertProfile.user_id == current_user.id
        ).first()

        profile_data = data.profile.dict()

        if existing_profile:
            # Update profile
            for key, value in profile_data.items():
                setattr(existing_profile, key, value)
        else:
            # Create new profile
            existing_profile = ExpertProfile(
                user_id=current_user.id, **profile_data
            )
            db.add(existing_profile)

        existing_weight = db.query(ExpertWeight).filter(
            ExpertWeight.user_id == current_user.id
        ).first()

        weight_data = data.weight.dict()

        if existing_weight:
            for key, value in weight_data.items():
                setattr(existing_weight, key, value)
        else:
            existing_weight = ExpertWeight(
                user_id=current_user.id, **weight_data
            )
            db.add(existing_weight)

        # COMMIT SEKALI SAJA
        db.commit()
        db.refresh(existing_profile)
        db.refresh(existing_weight)

        return {
            "profile": existing_profile,
            "weight": existing_weight
        }

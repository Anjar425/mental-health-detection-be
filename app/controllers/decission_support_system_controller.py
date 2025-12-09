from typing import List
from .base_controller import BaseController
from .preferences_controller import PreferencesController
from .expert_profiles_controller import ExpertProfilesController
from ..schemas import ExpertCapabilityIn, PreferenceItem
from ..models import AssessmentHistory
from app.controllers.decission_support_system.gdss import create_dynamic_consensus_model, calculate_patient_result
from fastapi import HTTPException, status

class DecissionSupportSystemController(BaseController):
    def convert_expert_preference(self):
        preferences = PreferencesController().get_all_preference()
        profiles = ExpertProfilesController().get_all_profiles()

        ed_map = {"S1": 1, "S2": 2, "S3": 3, "D1": 0, "D2": 0, "D3": 0}

        all_experts = []
        all_preferences = {}

        pref_map = {int(p["user_id"]): p["preferences"] for p in preferences}

        for p in profiles:
            user_id = int(p["user_id"])
            profile = p["profile"]
            weight = p["weight"]

            if user_id not in pref_map:
                continue

            user_pref_items = pref_map[user_id]
            if len(user_pref_items) != 21:
                continue

            if (
                profile["flight_hours"] is None or
                profile["patient_count"] is None or
                profile["education_level"] is None or
                profile["publication_count"] is None
            ):
                continue

            if (
                weight["flight_hours_weight"] is None or
                weight["patient_weight"] is None or
                weight["education_weight"] is None or
                weight["publication_weight"] is None
            ):
                continue

            expert = ExpertCapabilityIn(
                expert_id=str(user_id),

                JamTerbang=profile["flight_hours"],
                Patients=profile["patient_count"],
                Pendidikan=ed_map.get(profile["education_level"], 0),
                Publikasi=profile["publication_count"],

                weight_JamTerbang=weight["flight_hours_weight"],
                weight_Patients=weight["patient_weight"],
                weight_Pendidikan=weight["education_weight"],
                weight_Publikasi=weight["publication_weight"]
            )

            all_experts.append(expert)

            pref_list = [None] * 21
            for item in user_pref_items:
                idx = item["dass21_id"] - 1
                pref_list[idx] = PreferenceItem(
                    D=item["percent_depression"],
                    A=item["percent_anxiety"],
                    S=item["percent_stress"],
                )

            if any(x is None for x in pref_list):
                continue

            all_preferences[str(user_id)] = pref_list

        print(all_experts)
        return {
            "all_experts": all_experts,
            "all_preferences": all_preferences
        }

    
    def calculate_qdds(self, data: List[int], current_user=None, assessment_type: str = "21"):
        pref_data = self.convert_expert_preference()

        all_experts = pref_data["all_experts"]
        all_preferences = pref_data["all_preferences"]

        consensus_model = create_dynamic_consensus_model(
            all_experts=all_experts,
            all_preferences=all_preferences
        )
        # obtain DB session and ensure result is persisted before returning
        db = next(self.get_session())
        result = calculate_patient_result(
            patient_scores=data,
            consensus_model=consensus_model,
            db=db,
            user_id=(current_user.id if current_user is not None else None),
            assessment_type=assessment_type,
        )

        return result

    def get_user_history(self, current_user):
        """
        Retrieve assessment history for the current user, ordered by newest first.
        """
        db = next(self.get_session())
        records = (
            db.query(AssessmentHistory)
            .filter(AssessmentHistory.user_id == current_user.id)
            .order_by(AssessmentHistory.created_at.desc())
            .all()
        )
        return records

    def delete_history(self, history_id: int, current_user):
        """
        Delete an assessment history record if it belongs to the current user.
        """
        db = next(self.get_session())
        
        # Find the record
        record = db.query(AssessmentHistory).filter(
            AssessmentHistory.id == history_id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment history record not found"
            )
        
        # Check ownership
        if record.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this record"
            )
        
        # Delete and commit
        db.delete(record)
        db.commit()
        
        return {"message": "Assessment history deleted successfully", "id": history_id}    
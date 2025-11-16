from typing import List
from .base_controller import BaseController
from .preferences_controller import PreferencesController
from .expert_profiles_controller import ExpertProfilesController
from ..schemas import ExpertCapabilityIn, PreferenceItem
from app.controllers.decission_support_system.gdss import create_dynamic_consensus_model, calculate_patient_result

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

    
    def calculate_qdds(self, data: List[int]):
        pref_data = self.convert_expert_preference()

        all_experts = pref_data["all_experts"]
        all_preferences = pref_data["all_preferences"]

        consensus_model = create_dynamic_consensus_model(
            all_experts=all_experts,
            all_preferences=all_preferences
        )
        result = calculate_patient_result(patient_scores=data, consensus_model=consensus_model)

        return result

    
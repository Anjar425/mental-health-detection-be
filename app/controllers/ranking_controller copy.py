from .base_controller import BaseController
from sqlalchemy.orm import Session
from ..models import ExpertProfile, ExpertWeight, User
from sqlalchemy import func
from fastapi import HTTPException

class RankingController(BaseController):
    
    def _convert_education_to_score(self, education_str: str) -> int:
        """Helper untuk mengubah string pendidikan menjadi skor numerik"""
        if not education_str:
            return 1
        
        edu_lower = education_str.lower()
        if 's3' in edu_lower or 'doktor' in edu_lower or 'phd' in edu_lower:
            return 4
        elif 's2' in edu_lower or 'magister' in edu_lower or 'master' in edu_lower:
            return 3
        elif 's1' in edu_lower or 'sarjana' in edu_lower:
            return 2
        elif 'd3' in edu_lower or 'diploma' in edu_lower:
            return 1.5
        else:
            return 1 # Default

    def get_expert_rankings(self, current_user):
        db: Session = next(self.get_session())

        results = (
         db.query(ExpertProfile, ExpertWeight, User.email)
            .join(ExpertWeight, ExpertProfile.user_id == ExpertWeight.user_id)
            .join(User, ExpertProfile.user_id == User.id)
            .filter(ExpertProfile.user_id == current_user.id)  # <-- filter hanya user yang login
            .all()
        )

        if not results:
            return []

        # 2. Persiapkan Data Mentah & Hitung Rata-rata Bobot Global
        processed_data = []
        total_weights = {
            "education": 0,
            "patient": 0,
            "publication": 0,
            "flight_hours": 0
        }
        
        # Variabel untuk mencari nilai MAX (untuk normalisasi)
        max_values = {
            "education": 0,
            "patient": 0,
            "publication": 0,
            "flight_hours": 0
        }

        count = len(results)

        for profile, weight, email in results:
            # Konversi pendidikan ke angka
            edu_score = self._convert_education_to_score(profile.education_level)
            
            # Update Max Values
            max_values["education"] = max(max_values["education"], edu_score)
            max_values["patient"] = max(max_values["patient"], profile.patient_count or 0)
            max_values["publication"] = max(max_values["publication"], profile.publication_count or 0)
            max_values["flight_hours"] = max(max_values["flight_hours"], profile.flight_hours or 0)

            # Sum Weights (untuk nanti dirata-rata)
            total_weights["education"] += weight.education_weight or 0
            total_weights["patient"] += weight.patient_weight or 0
            total_weights["publication"] += weight.publication_weight or 0
            total_weights["flight_hours"] += weight.flight_hours_weight or 0

            processed_data.append({
                "email": email,
                "raw": {
                    "education": edu_score,
                    "patient": profile.patient_count or 0,
                    "publication": profile.publication_count or 0,
                    "flight_hours": profile.flight_hours or 0
                },
                "original_profile": {
                    "education_level": profile.education_level
                }
            })

        # 3. Hitung Rata-rata Bobot (Global Weights)
        # Jika count 0, hindari pembagian nol (sudah dihandle di 'if not results')
        avg_weights = {
            "education": total_weights["education"] / count,
            "patient": total_weights["patient"] / count,
            "publication": total_weights["publication"] / count,
            "flight_hours": total_weights["flight_hours"] / count
        }

        # 4. Normalisasi & Perhitungan Skor Akhir (SAW Method)
        ranked_experts = []

        for item in processed_data:
            # Normalisasi (Nilai / Max) -> Jika Max 0, nilai 0
            norm_edu = item["raw"]["education"] / max_values["education"] if max_values["education"] > 0 else 0
            norm_pat = item["raw"]["patient"] / max_values["patient"] if max_values["patient"] > 0 else 0
            norm_pub = item["raw"]["publication"] / max_values["publication"] if max_values["publication"] > 0 else 0
            norm_fly = item["raw"]["flight_hours"] / max_values["flight_hours"] if max_values["flight_hours"] > 0 else 0

            # Hitung Skor: (Normalisasi * Rata2 Bobot)
            final_score = (
                (norm_edu * avg_weights["education"]) +
                (norm_pat * avg_weights["patient"]) +
                (norm_pub * avg_weights["publication"]) +
                (norm_fly * avg_weights["flight_hours"])
            )

            ranked_experts.append({
                "expert_email": item["email"],
                "score": round(final_score, 2), # Pembulatan 2 desimal
                "details": {
                    "education_str": item["original_profile"]["education_level"],
                    "normalized_scores": {
                        "education": round(norm_edu, 2),
                        "patient": round(norm_pat, 2),
                        "publication": round(norm_pub, 2),
                        "flight_hours": round(norm_fly, 2)
                    }
                }
            })

        # 5. Urutkan dari skor tertinggi ke terendah
        ranked_experts.sort(key=lambda x: x["score"], reverse=True)

        return {
            "global_average_weights": avg_weights,
            "rankings": ranked_experts
        }
        
    def get_my_ranking(self, current_user):
        db: Session = next(self.get_session())

        rankings_data = self.get_expert_rankings()
        rankings = rankings_data.get("rankings", [])

        # Cari peringkat user saat ini
        for idx, expert in enumerate(rankings):
            if expert["expert_email"] == current_user.email:
                return {
                    "rank": idx + 1,  # Peringkat dimulai dari 1
                    "total_experts": len(rankings),
                    "score": expert["score"],
                    "details": expert["details"]
                }

        raise HTTPException(status_code=404, detail="Ranking for current user not found")
from collections import defaultdict
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from .base_controller import BaseController
from ..models.expert_group import ExpertGroup
from ..models.expert_profiles import ExpertProfile
from ..models.expert_weight import ExpertWeight
from ..models.preference import Preference
from ..models.user import User
from ..models.group_weight import GroupWeight
from ..schemas.expert_group import ExpertGroupCreate, ExpertGroupUpdate
from ..schemas.group_ranking import (
    ExpertCapabilityOut,
    ExpertPreferenceOut,
    GroupConsensusOut,
    GroupExpertRankingOut,
    GroupRankingResponse,
)
from ..controllers.decission_support_system_controller import CALIBRATION_DATASET, FALLBACK_PROFILES, FALLBACK_PREFS


# Copy CALIBRATION_DATASET locally to avoid import issues
CALIBRATION_DATASET_LOCAL = [
    [0, 2, 1, 3, 2, 1, 1, 0, 1, 1, 3, 0, 1, 1, 3, 2, 3, 0, 1, 2, 2],
    [2, 1, 1, 2, 3, 2, 1, 0, 2, 2, 1, 3, 2, 3, 1, 1, 0, 0, 0, 1, 3],
    [1, 1, 1, 0, 3, 2, 2, 2, 1, 1, 3, 2, 1, 2, 0, 2, 3, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 3, 1, 0],
    [2, 1, 3, 0, 3, 3, 0, 3, 0, 2, 0, 3, 3, 2, 0, 3, 3, 3, 2, 0, 0],
    [1, 1, 0, 2, 3, 0, 0, 0, 2, 3, 2, 1, 0, 2, 2, 2, 1, 2, 2, 2, 1],
    [0, 2, 1, 2, 1, 0, 2, 3, 1, 3, 3, 1, 1, 0, 3, 3, 2, 0, 2, 1, 3],
    [2, 0, 0, 3, 0, 2, 1, 1, 1, 1, 0, 3, 2, 2, 3, 1, 0, 3, 0, 3, 1],
    [0, 1, 3, 1, 1, 3, 0, 1, 1, 1, 1, 2, 2, 2, 2, 0, 1, 3, 0, 0, 0],
    [0, 1, 0, 3, 1, 1, 1, 3, 2, 1, 1, 0, 1, 3, 1, 0, 2, 1, 0, 2, 0],
    [3, 0, 0, 0, 1, 3, 0, 3, 0, 0, 1, 3, 0, 3, 0, 1, 1, 0, 2, 2, 2],
    [1, 0, 0, 0, 1, 3, 1, 2, 1, 3, 3, 3, 2, 3, 2, 1, 2, 2, 3, 1, 3],
    [2, 3, 3, 2, 2, 2, 2, 2, 1, 1, 2, 3, 0, 3, 2, 2, 0, 2, 0, 0, 3],
    [1, 0, 1, 0, 0, 1, 1, 1, 2, 0, 1, 2, 2, 0, 3, 2, 1, 1, 2, 0, 2],
    [2, 1, 3, 3, 2, 2, 2, 2, 3, 3, 0, 3, 0, 2, 3, 2, 0, 3, 2, 1, 0],
    [1, 2, 1, 2, 1, 2, 2, 3, 1, 2, 1, 3, 1, 1, 2, 1, 0, 0, 3, 3, 3],
    [1, 0, 3, 3, 3, 0, 2, 0, 0, 0, 1, 0, 1, 2, 2, 0, 2, 1, 1, 2, 2],
    [0, 2, 3, 0, 3, 1, 0, 1, 2, 1, 3, 2, 2, 1, 3, 2, 2, 1, 0, 0, 0],
    [1, 3, 1, 2, 0, 0, 1, 2, 0, 0, 0, 3, 2, 1, 0, 0, 0, 2, 1, 1, 0],
    [3, 2, 0, 2, 0, 1, 2, 3, 1, 3, 2, 2, 0, 0, 1, 2, 2, 1, 3, 2, 0],
]


def education_from_code(code: int) -> str:
    mapping = {1: "Diploma", 2: "Sarjana (S1)", 3: "Magister (S2)", 4: "Doktor (S3)"}
    return mapping.get(code, "Profesional")


def education_to_number(level: str) -> int:
    normalized = (level or "").strip()
    mapping = {
        "Diploma": 1,
        "Sarjana (S1)": 2,
        "Sarjana": 2,
        "S1": 2,
        "Magister (S2)": 3,
        "Magister": 3,
        "S2": 3,
        "Doktor (S3)": 4,
        "Doktor": 4,
        "S3": 4,
    }
    return mapping.get(normalized, 2)


def normalize_values(values: List[float]) -> List[float]:
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return [1.0] * len(values)
    return [(value - minimum) / (maximum - minimum) for value in values]


def normalize_weight_vector(weights: List[float]) -> List[float]:
    total = sum(weights)
    if total <= 0:
        return [0.25, 0.25, 0.25, 0.25]
    return [weight / total for weight in weights]


def fuzzy_iowa_for_item(crisp_prefs, expert_weights):
    import numpy as np
    n = len(crisp_prefs)
    if n == 0 or n != len(expert_weights):
        return 0.0
    order = np.argsort(expert_weights)[::-1]
    ordered_prefs = np.array(crisp_prefs)[order]
    owa_weights = np.array(expert_weights)[order]
    agg_score = np.sum(owa_weights * ordered_prefs)
    return float(np.clip(agg_score, 0.0, 1.0))


def _qgdd_from_pref_vector(pref_vector):
    """
    Quantum Global Consensus Degree (QGDD) - Derajat kesepakatan global.
    Mengukur seberapa konsisten preferensi antar item.
    """
    import numpy as np
    if not pref_vector or len(pref_vector) == 0:
        return 0.0
    pref_array = np.array(pref_vector)
    mean_pref = np.mean(pref_array)
    variance = np.var(pref_array)
    # QGDD = 1 - variance (semakin kecil variance, semakin konsisten)
    return 1.0 - variance if variance <= 1.0 else 0.0


def _compute_gap(a_norm):
    """
    Gap: Jarak antar alternatif ranking.
    Semakin besar gap, semakin tegas keputusannya.
    """
    import numpy as np
    if len(a_norm) < 2:
        return 0.0
    sorted_a = np.sort(a_norm)[::-1]  # Descending
    return sorted_a[0] - sorted_a[1] if len(sorted_a) > 1 else 0.0


def _entropy_dist(weights):
    """
    Fairness: Entropi dari distribusi bobot pakar.
    Semakin tinggi entropi, semakin adil pembagian bobotnya.
    """
    import numpy as np
    weights = np.array(weights)
    weights = weights[weights > 0]  # Avoid log(0)
    if len(weights) == 0:
        return 0.0
    entropy = -np.sum(weights * np.log(weights))
    # Normalize by max entropy (uniform distribution)
    max_entropy = np.log(len(weights))
    return entropy / max_entropy if max_entropy > 0 else 0.0


def _integrate_patient_score(per_item_agg, patient_scores):
    """
    Integrasi skor pasien dengan agregasi preferensi.
    patient_scores: list of 21 integers (0-3 scale)
    per_item_agg: list of 21 vectors [D, A, S] probabilities
    """
    import numpy as np
    if len(patient_scores) != 21 or len(per_item_agg) != 21:
        return np.array([0.0, 0.0, 0.0])
    
    final_scores = np.zeros(3)
    for i in range(21):
        score = patient_scores[i]
        probs = per_item_agg[i]  # [D_prob, A_prob, S_prob]
        final_scores += score * probs
    
    # Normalize
    total = np.sum(final_scores)
    return final_scores / total if total > 0 else np.array([1/3, 1/3, 1/3])


def _evaluate_fitness_group(weights_norm, eta, lambda_dist, expert_prefs, patient_scores_batch, n_experts, n_items, n_alts):
    """
    Fungsi Fitness untuk Grup (Sesuai Skripsi).
    """
    import numpy as np
    
    # 1. Normalisasi Bobot
    w_sum = weights_norm.sum()
    weights_norm = weights_norm / w_sum if w_sum > 1e-9 else np.ones(n_experts)/n_experts
    
    # 2. Agregasi Preferensi (Fuzzy IOWA)
    per_item_agg = []
    for q in range(n_items):
        alt_agg = []
        for k in range(n_alts):
            prefs_alt = [expert_prefs[e][q][['d','a','s'][k]]/100.0 for e in range(n_experts)]
            agg = fuzzy_iowa_for_item(prefs_alt, weights_norm)
            alt_agg.append(agg)
        v = np.array(alt_agg)
        v_sum = v.sum()
        per_item_agg.append((v / v_sum) if v_sum > 1e-9 else np.zeros(n_alts))
    
    # 3. Model Quality
    qgdd_scores = [_qgdd_from_pref_vector([per_item_agg[i][k] for i in range(n_items)]) for k in range(n_alts)]
    a_norm = np.array(qgdd_scores)
    gap = _compute_gap(a_norm)
    fair = _entropy_dist(weights_norm)
    model_quality = (1 - eta) * gap + eta * fair
    
    # 4. Penalti Distribusi
    penalty = 0.0
    if patient_scores_batch and len(patient_scores_batch) > 1:
        all_diagnoses = []
        for scores in patient_scores_batch:
            final_scores = _integrate_patient_score(per_item_agg, scores)
            all_diagnoses.append(np.argmax(final_scores))
        counts = [all_diagnoses.count(i) for i in range(n_alts)]
        penalty_raw = np.std(counts)
        penalty = penalty_raw / (len(patient_scores_batch) / 1.5)
    
    # 5. Fitness Akhir (sebelumnya)
    final_fitness = model_quality - (lambda_dist * penalty)
    return final_fitness, per_item_agg


def run_ga_optimization(expert_prefs: List[List[Dict[str, float]]], n_generations=50, pop_size=20):
    """
    GA to optimize expert weights based on preferences, using fitness from thesis calibration data.
    Fitness: minimize variance in predicted DASS scores across 20 calibration samples.
    Hyperparameters: 50 generations, population 20 (as per thesis setup).
    """
    import numpy as np
    import random
    import logging
    
    logging.info(f"Starting GA optimization with {len(expert_prefs)} experts, {len(expert_prefs[0]) if expert_prefs else 0} questions")
    
    n_experts = len(expert_prefs)
    if n_experts == 0 or not expert_prefs[0]:
        logging.warning("No experts or preferences, returning equal weights")
        return np.ones(n_experts) / n_experts
    
    # Initialize population: random weights summing to 1
    population = []
    for _ in range(pop_size):
        weights = np.random.random(n_experts)
        weights /= weights.sum()
        population.append(weights)
    
    for gen in range(n_generations):
        # Evaluate fitness using new thesis method
        fitnesses = []
        for weights in population:
            fitness_value, _ = _evaluate_fitness_group(
                weights, 0.25, 0.8, expert_prefs, CALIBRATION_DATASET_LOCAL, n_experts, len(expert_prefs[0]), 3
            )
            fitnesses.append(fitness_value)
        
        # Selection: keep top individuals
        sorted_idx = np.argsort(fitnesses)[::-1]
        selected = [population[i] for i in sorted_idx[:max(1, pop_size//2)]]
        
        # Crossover and mutation to fill population
        new_pop = selected[:]
        while len(new_pop) < pop_size:
            if len(selected) >= 2:
                p1, p2 = random.sample(selected, 2)
            else:
                # If only one selected, use it with a random individual
                p1 = selected[0]
                p2 = np.random.random(n_experts)
                p2 /= p2.sum()
            
            # Simple crossover
            cross_point = random.randint(1, n_experts-1)
            child = np.concatenate([p1[:cross_point], p2[cross_point:]])
            child /= child.sum()
            
            # Mutation
            if random.random() < 0.1:
                j = random.randint(0, n_experts-1)
                child[j] += np.random.normal(0, 0.1)
                child = np.clip(child, 0, 1)
                child /= child.sum()
            new_pop.append(child)
        population = new_pop
    
    # Best weights
    best_weights = population[0]
    # Ensure no expert contribution is exactly zero: apply floor and renormalize
    def ensure_minimum_weights(vec, min_w=0.01):
        vec = np.array(vec, dtype=float)
        n = len(vec)
        if min_w * n >= 1.0:
            vec = np.maximum(vec, 1e-6)
            vec /= vec.sum()
            return vec
        v = np.maximum(vec, min_w)
        v /= v.sum()
        return v

    best_weights = ensure_minimum_weights(best_weights, min_w=0.01)
    logging.info(f"GA completed, best weights: {best_weights}")
    return best_weights


def build_preferences(
    pref_lookup: Dict[int, Preference],
    fallback_pref: List[Dict[str, float]],
) -> List[ExpertPreferenceOut]:
    preferences: List[ExpertPreferenceOut] = []
    for question_id in range(1, 22):
        if pref_lookup and question_id in pref_lookup:
            pref_row = pref_lookup[question_id]
            preferences.append(
                ExpertPreferenceOut(
                    question_id=question_id,
                    depression=float(pref_row.percent_depression or 0),
                    anxiety=float(pref_row.percent_anxiety or 0),
                    stress=float(pref_row.percent_stress or 0),
                )
            )
        else:
            fallback_values = (
                fallback_pref[question_id - 1]
                if question_id - 1 < len(fallback_pref)
                else {"d": 33, "a": 33, "s": 34}
            )
            preferences.append(
                ExpertPreferenceOut(
                    question_id=question_id,
                    depression=float(fallback_values.get("d", 0)),
                    anxiety=float(fallback_values.get("a", 0)),
                    stress=float(fallback_values.get("s", 0)),
                )
            )
    return preferences


def aggregate_consensus(entries: List[Dict[str, object]]) -> List[GroupConsensusOut]:
    consensus: List[GroupConsensusOut] = []
    for question_id in range(1, 22):
        # Collect preferences for this question
        depression_prefs = []
        anxiety_prefs = []
        stress_prefs = []
        weights = []
        
        for entry in entries:
            pref = next((item for item in entry["preferences"] if item.question_id == question_id), None)
            if pref:
                depression_prefs.append(pref.depression / 100.0)  # Convert to 0-1
                anxiety_prefs.append(pref.anxiety / 100.0)
                stress_prefs.append(pref.stress / 100.0)
                weights.append(entry["weight_ratio"])
        
        if not weights:
            depression = anxiety = stress = 0.0
        else:
            # Use Fuzzy IOWA for aggregation
            depression = fuzzy_iowa_for_item(depression_prefs, weights)
            anxiety = fuzzy_iowa_for_item(anxiety_prefs, weights)
            stress = fuzzy_iowa_for_item(stress_prefs, weights)
            
            # Convert back to 0-100 scale
            depression *= 100.0
            anxiety *= 100.0
            stress *= 100.0

        consensus.append(
            GroupConsensusOut(
                question_id=question_id,
                depression=round(depression, 2),
                anxiety=round(anxiety, 2),
                stress=round(stress, 2),
            )
        )
    return consensus


def build_dummy_response(group: ExpertGroup) -> GroupRankingResponse:
    dummy_preferences = [
        ExpertPreferenceOut(question_id=question_id, depression=30.0, anxiety=35.0, stress=35.0)
        for question_id in range(1, 22)
    ]
    dummy_ranking = GroupExpertRankingOut(
        user_id=1,
        username="Dummy Expert",
        email="dummy@example.com",
        influence_score=100.0,
        influence_percent=100.0,
        capability=ExpertCapabilityOut(
            education_level="Sarjana",
            publication_count=5,
            patient_count=100,
            flight_hours=200,
            weight_JT=25.0,
            weight_Pat=25.0,
            weight_Pend=25.0,
            weight_Pub=25.0,
        ),
        preferences=dummy_preferences,
        rank=1,
    )
    dummy_consensus = [
        GroupConsensusOut(question_id=question_id, depression=30.0, anxiety=35.0, stress=35.0)
        for question_id in range(1, 22)
    ]
    return GroupRankingResponse(
        group_id=group.id,
        group_name=group.name,
        description=group.description,
        rankings=[dummy_ranking],
        consensus_matrix=dummy_consensus,
    )


class ExpertGroupController(BaseController):
    def create_group(self, data: ExpertGroupCreate):
        db: Session = next(self.get_session())
        if not data.expert_ids or len(data.expert_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 experts are required to create a group.")
        experts = (
            db.query(User)
            .filter(User.id.in_(data.expert_ids), User.role == "expert")
            .all()
        )
        if len(experts) != len(set(data.expert_ids)):
            raise HTTPException(status_code=400, detail="Some expert IDs not found or not experts.")
        group = ExpertGroup(name=data.name, description=data.description)
        group.experts = experts
        db.add(group)
        db.commit()
        db.refresh(group)
        return group

    def update_group(self, group_id: int, data: ExpertGroupUpdate):
        db: Session = next(self.get_session())
        group = db.query(ExpertGroup).filter(ExpertGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if data.name is not None:
            group.name = data.name
        if data.description is not None:
            group.description = data.description
        db.commit()
        db.refresh(group)
        return group

    def delete_group(self, group_id: int):
        db: Session = next(self.get_session())
        group = db.query(ExpertGroup).filter(ExpertGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        db.delete(group)
        db.commit()
        # Invalidate cached weights
        try:
            db.query(GroupWeight).filter(GroupWeight.group_id == group_id).delete()
            db.commit()
        except Exception:
            db.rollback()
        return {"message": "Group deleted"}

    def add_expert_to_group(self, group_id: int, expert_id: int):
        db: Session = next(self.get_session())
        group = db.query(ExpertGroup).filter(ExpertGroup.id == group_id).first()
        expert = db.query(User).filter(User.id == expert_id, User.role == "expert").first()
        if not group or not expert:
            raise HTTPException(status_code=404, detail="Group or expert not found")
        if expert in group.experts:
            raise HTTPException(status_code=400, detail="Expert already in group")
        group.experts.append(expert)
        db.commit()
        # Invalidate cached weights for this group
        try:
            db.query(GroupWeight).filter(GroupWeight.group_id == group_id).delete()
            db.commit()
        except Exception:
            db.rollback()
        return group

    def remove_expert_from_group(self, group_id: int, expert_id: int):
        db: Session = next(self.get_session())
        group = db.query(ExpertGroup).filter(ExpertGroup.id == group_id).first()
        expert = db.query(User).filter(User.id == expert_id, User.role == "expert").first()
        if not group or not expert:
            raise HTTPException(status_code=404, detail="Group or expert not found")
        if expert not in group.experts:
            raise HTTPException(status_code=400, detail="Expert not in group")
        group.experts.remove(expert)
        db.commit()
        # Invalidate cached weights for this group
        try:
            db.query(GroupWeight).filter(GroupWeight.group_id == group_id).delete()
            db.commit()
        except Exception:
            db.rollback()
        return group

    def invalidate_group_weights(self, group_id: int):
        """Invalidate cached GA weights for a group (admin action)."""
        db: Session = next(self.get_session())
        try:
            deleted = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).delete()
            db.commit()
            return {"deleted": int(deleted)}
        finally:
            db.close()

    def recompute_group_weights(self, group_id: int):
        """Force recompute GA weights for a group and persist result (admin action).

        This deletes any existing cached GroupWeight and then invokes the standard
        ranking computation (which will run the GA and save the new weights).
        Returns the persisted weights and signature.
        """
        db: Session = next(self.get_session())
        group = db.query(ExpertGroup).filter(ExpertGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        try:
            # Remove any existing cached weights so get_group_rankings will recompute
            db.query(GroupWeight).filter(GroupWeight.group_id == group_id).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        # Call existing ranking computation which will run GA and persist weights
        try:
            self.get_group_rankings(group_id)
        except Exception as exc:
            # Propagate as HTTP 500 for admin visibility
            raise HTTPException(status_code=500, detail=f"Failed to recompute weights: {exc}")

        # Read back persisted GroupWeight
        db = next(self.get_session())
        try:
            gw = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).order_by(GroupWeight.created_at.desc()).first()
            if not gw or not gw.weights:
                raise HTTPException(status_code=500, detail="Recompute finished but persisted weights not found")
            import json
            weights = json.loads(gw.weights)
            try:
                meta_parsed = json.loads(gw.meta) if gw.meta else None
            except Exception:
                meta_parsed = None
            return {"weights": weights, "signature": gw.signature, "created_at": (gw.created_at.isoformat() if getattr(gw, 'created_at', None) else None), "meta": meta_parsed}
        finally:
            db.close()

    def get_group_signature_info(self, group_id: int):
        """Return computed and stored signature and weights_info for debugging (admin only)."""
        db: Session = next(self.get_session())
        group = (
            db.query(ExpertGroup)
            .options(joinedload(ExpertGroup.experts))
            .filter(ExpertGroup.id == group_id)
            .first()
        )
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        experts = sorted(group.experts, key=lambda expert: expert.id)
        user_ids = [expert.id for expert in experts]

        preference_rows = db.query(Preference).filter(Preference.user_id.in_(user_ids)).all()
        preference_map: Dict[int, Dict[int, Preference]] = defaultdict(dict)
        for row in preference_rows:
            if row.dass21_id:
                preference_map[row.user_id][row.dass21_id] = row

        # build expert_rows similar to get_group_rankings
        def fallback_profile(index: int) -> Dict[str, float]:
            fallback_profile_keys: List[int] = sorted(FALLBACK_PROFILES.keys())
            key = fallback_profile_keys[index % len(fallback_profile_keys)] if fallback_profile_keys else 0
            return FALLBACK_PROFILES[key]

        def fallback_preferences(index: int) -> List[Dict[str, float]]:
            fallback_pref_keys: List[int] = sorted(FALLBACK_PREFS.keys())
            key = fallback_pref_keys[index % len(fallback_pref_keys)] if fallback_pref_keys else 0
            return FALLBACK_PREFS[key]

        expert_rows: List[Dict[str, object]] = []
        for idx, expert in enumerate(experts):
            profile = db.query(ExpertProfile).filter(ExpertProfile.user_id == expert.id).first()
            default_profile = fallback_profile(idx)

            if profile:
                education_label = profile.education_level or education_from_code(int(default_profile.get("Pend", 2)))
                publication_count = int(profile.publication_count or default_profile.get("Pub", 0) or 0)
                patient_count = int(profile.patient_count or default_profile.get("Pat", 0) or 0)
                experience_years = int(profile.flight_hours or default_profile.get("JT", 0) or 0)
            else:
                education_label = education_from_code(int(default_profile.get("Pend", 2)))
                publication_count = int(default_profile.get("Pub", 0) or 0)
                patient_count = int(default_profile.get("Pat", 0) or 0)
                experience_years = int(default_profile.get("JT", 0) or 0)

            weight_record = db.query(ExpertWeight).filter(ExpertWeight.user_id == expert.id).first()
            raw_weights = [
                float((weight_record.flight_hours_weight if weight_record else None) or default_profile.get("W_JT", 25) or 0),
                float((weight_record.patient_weight if weight_record else None) or default_profile.get("W_Pat", 25) or 0),
                float((weight_record.education_weight if weight_record else None) or default_profile.get("W_Pend", 25) or 0),
                float((weight_record.publication_weight if weight_record else None) or default_profile.get("W_Pub", 25) or 0),
            ]

            pref_lookup = preference_map.get(expert.id)
            fallback_pref = fallback_preferences(idx)

            expert_rows.append(
                {
                    "user_id": expert.id,
                    "username": expert.username,
                    "email": expert.email,
                    "education_label": education_label,
                    "publication_count": publication_count,
                    "patient_count": patient_count,
                    "experience_years": experience_years,
                    "raw_weights": raw_weights,
                    "preferences": build_preferences(pref_lookup, fallback_pref),
                }
            )

        # compute signature (same method as in get_group_rankings)
        canon = []
        for e in expert_rows:
            uid = int(e["user_id"])
            raw_weights = [round(float(x), 3) for x in e.get("raw_weights", [])]
            prefs = []
            for p in e.get("preferences", []):
                prefs.append(
                    {
                        "q": int(p.question_id),
                        "d": int(round(float(getattr(p, "depression", 0)))),
                        "a": int(round(float(getattr(p, "anxiety", 0)))),
                        "s": int(round(float(getattr(p, "stress", 0)))),
                    }
                )
            canon.append({"user_id": uid, "raw_weights": raw_weights, "preferences": prefs})
        canon_sorted = sorted(canon, key=lambda x: int(x["user_id"]))
        sig_raw = json.dumps(canon_sorted, sort_keys=True, separators=(",", ":"))
        computed_signature = __import__('hashlib').sha256(sig_raw.encode('utf-8')).hexdigest()

        gw = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).order_by(GroupWeight.created_at.desc()).first()
        try:
            try:
                meta_parsed = json.loads(gw.meta) if gw and gw.meta else None
            except Exception:
                meta_parsed = None

            weights_info = {
                "computed_signature": computed_signature,
                "stored_signature": (gw.signature if gw else None),
                "weights_by_user": meta_parsed.get("weights_by_user") if meta_parsed else None,
            }
            return weights_info
        finally:
            db.close()

    def get_all_groups(self):
        db: Session = next(self.get_session())
        groups = db.query(ExpertGroup).all()
        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at,
                "member_count": len(group.experts),
            }
            for group in groups
        ]

    def get_group_with_members(self, group_id: int):
        db: Session = next(self.get_session())
        group = (
            db.query(ExpertGroup)
            .options(joinedload(ExpertGroup.experts))
            .filter(ExpertGroup.id == group_id)
            .first()
        )
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group

    def get_group_rankings(self, group_id: int) -> GroupRankingResponse:
        """
        Get group rankings. Uses cached GA weights if group membership/preferences unchanged.
        """

        db: Session = next(self.get_session())
        group = (
            db.query(ExpertGroup)
            .options(joinedload(ExpertGroup.experts))
            .filter(ExpertGroup.id == group_id)
            .first()
        )
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        experts = sorted(group.experts, key=lambda expert: expert.id)
        if not experts:
            return GroupRankingResponse(
                group_id=group.id,
                group_name=group.name,
                description=group.description,
                rankings=[],
                consensus_matrix=[],
            )

        user_ids = [expert.id for expert in experts]
        profile_map: Dict[int, ExpertProfile] = {
            profile.user_id: profile
            for profile in db.query(ExpertProfile).filter(ExpertProfile.user_id.in_(user_ids)).all()
        }
        weight_map: Dict[int, ExpertWeight] = {
            weight.user_id: weight
            for weight in db.query(ExpertWeight).filter(ExpertWeight.user_id.in_(user_ids)).all()
        }
        preference_rows = db.query(Preference).filter(Preference.user_id.in_(user_ids)).all()
        preference_map: Dict[int, Dict[int, Preference]] = defaultdict(dict)
        for row in preference_rows:
            if row.dass21_id:
                preference_map[row.user_id][row.dass21_id] = row

        fallback_profile_keys: List[int] = sorted(FALLBACK_PROFILES.keys())
        fallback_pref_keys: List[int] = sorted(FALLBACK_PREFS.keys())

        def fallback_profile(index: int) -> Dict[str, float]:
            key = fallback_profile_keys[index % len(fallback_profile_keys)] if fallback_profile_keys else 0
            return FALLBACK_PROFILES[key]

        def fallback_preferences(index: int) -> List[Dict[str, float]]:
            key = fallback_pref_keys[index % len(fallback_pref_keys)] if fallback_pref_keys else 0
            return FALLBACK_PREFS[key]

        expert_rows: List[Dict[str, object]] = []

        for idx, expert in enumerate(experts):
            profile = profile_map.get(expert.id)
            default_profile = fallback_profile(idx)

            if profile:
                education_label = profile.education_level or education_from_code(int(default_profile.get("Pend", 2)))
                publication_count = int(profile.publication_count or default_profile.get("Pub", 0) or 0)
                patient_count = int(profile.patient_count or default_profile.get("Pat", 0) or 0)
                experience_years = int(profile.flight_hours or default_profile.get("JT", 0) or 0)
            else:
                education_label = education_from_code(int(default_profile.get("Pend", 2)))
                publication_count = int(default_profile.get("Pub", 0) or 0)
                patient_count = int(default_profile.get("Pat", 0) or 0)
                experience_years = int(default_profile.get("JT", 0) or 0)

            weight_record = weight_map.get(expert.id)
            raw_weights = [
                float((weight_record.flight_hours_weight if weight_record else None) or default_profile.get("W_JT", 25) or 0),
                float((weight_record.patient_weight if weight_record else None) or default_profile.get("W_Pat", 25) or 0),
                float((weight_record.education_weight if weight_record else None) or default_profile.get("W_Pend", 25) or 0),
                float((weight_record.publication_weight if weight_record else None) or default_profile.get("W_Pub", 25) or 0),
            ]

            pref_lookup = preference_map.get(expert.id)
            fallback_pref = fallback_preferences(idx)

            expert_rows.append(
                {
                    "user_id": expert.id,
                    "username": expert.username,
                    "email": expert.email,
                    "education_label": education_label,
                    "publication_count": publication_count,
                    "patient_count": patient_count,
                    "experience_years": experience_years,
                    "raw_weights": raw_weights,
                    "preferences": build_preferences(pref_lookup, fallback_pref),
                }
            )

        if not expert_rows:
            return build_dummy_response(group)

        # Extract preferences for GA optimization
        expert_prefs = [row["preferences"] for row in expert_rows]
        # Convert to list of dicts for GA
        prefs_for_ga = []
        for prefs in expert_prefs:
            q_prefs = []
            for p in prefs:
                q_prefs.append({'d': p.depression, 'a': p.anxiety, 's': p.stress})
            prefs_for_ga.append(q_prefs)

        # Run GA to optimize weights OR reuse cached if no change in group
        import logging
        import json
        import hashlib
        from ..models.group_weight import GroupWeight

        def compute_signature(entries):
            # Deterministic signature based on members data using canonical JSON.
            # Build a structured, sorted representation to avoid float and ordering issues.
            canon = []
            for e in entries:
                uid = int(e["user_id"])
                raw_weights = [round(float(x), 3) for x in e.get("raw_weights", [])]
                prefs = []
                for p in e.get("preferences", []):
                    prefs.append(
                        {
                            "q": int(p.question_id),
                            "d": int(round(float(getattr(p, "depression", 0)))),
                            "a": int(round(float(getattr(p, "anxiety", 0)))),
                            "s": int(round(float(getattr(p, "stress", 0)))),
                        }
                    )
                canon.append({"user_id": uid, "raw_weights": raw_weights, "preferences": prefs})
            # Sort by user_id to ensure deterministic order
            canon_sorted = sorted(canon, key=lambda x: int(x["user_id"]))
            sig_raw = json.dumps(canon_sorted, sort_keys=True, separators=(",", ":"))
            return hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()

        signature = compute_signature(expert_rows)
        db: Session = next(self.get_session())
        try:
            # Use the most recent persisted GroupWeight row
            gw = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).order_by(GroupWeight.created_at.desc()).first()
            logging.info(f"Group {group_id} signature computed={signature} stored={(gw.signature if gw else None)}")

            optimal_weights = None

            # If there is a persisted weights row, try to use it. Enforce preference for
            # per-user mapping (weights_by_user) if it contains weights for all current experts.
            if gw and gw.weights:
                try:
                    stored = json.loads(gw.weights)
                except Exception:
                    stored = None

                try:
                    meta_parsed_local = json.loads(gw.meta) if gw.meta else {}
                except Exception:
                    meta_parsed_local = {}

                weights_by_user_map = {}
                if isinstance(meta_parsed_local, dict) and meta_parsed_local.get("weights_by_user"):
                    for it in meta_parsed_local.get("weights_by_user", []):
                        try:
                            weights_by_user_map[int(it.get("user_id"))] = float(it.get("weight"))
                        except Exception:
                            continue

                import numpy as np

                # If any per-user mapping exists, prefer stored values per user where present
                if weights_by_user_map:
                    optimal_weights = np.array(
                        [weights_by_user_map.get(int(row["user_id"]), (float(stored[idx]) if stored and idx < len(stored) else 0.0)) for idx, row in enumerate(expert_rows)],
                        dtype=float,
                    )
                    try:
                        if np.any(np.isnan(optimal_weights)):
                            raise ValueError("Stored per-user weights contain NaN")
                    except Exception:
                        logging.info("Stored per-user weights invalid (NaN detected), will recompute")
                        optimal_weights = None
                    else:
                        logging.info(f"Using stored per-user weights for group {group_id} from DB (enforced for available users)")

                # Fallback: if full stored array exists and length matches, use it
                elif stored and isinstance(stored, list) and len(stored) == len(expert_rows):
                    try:
                        stored_arr = np.array(stored, dtype=float)
                        if not np.any(np.isnan(stored_arr)):
                            optimal_weights = stored_arr
                            logging.info(f"Using stored weights list for group {group_id}")
                    except Exception:
                        logging.info("Stored weights invalid (not numeric), will recompute")

                else:
                    logging.info("No valid stored weights mapping/list found, will recompute GA")

        finally:
            db.close()

        weights_info = None

        if optimal_weights is None:
            logging.info(f"Running GA for group {group_id} with {len(prefs_for_ga)} experts")
            optimal_weights = run_ga_optimization(prefs_for_ga)
            logging.info(f"Optimal weights from GA for group {group_id}: {optimal_weights}")
            # store into DB
            db = next(self.get_session())
            try:
                gw = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).order_by(GroupWeight.created_at.desc()).first()
                if not gw:
                    gw = GroupWeight(group_id=group_id)
                    gw.created_at = __import__('datetime').datetime.utcnow()
                    db.add(gw)
                # Build per-user mapping for permanence
                weights_list = [float(x) for x in optimal_weights.tolist()]
                weights_by_user = [
                    {"user_id": int(row["user_id"]), "weight": float(weights_list[idx])}
                    for idx, row in enumerate(expert_rows)
                ]

                gw.weights = json.dumps(weights_list)
                gw.signature = signature
                # optional metadata: record that this was produced by normal GA run and include mapping
                gw.meta = json.dumps({"source": "ga_run", "n_experts": len(expert_rows), "weights_by_user": weights_by_user})
                db.commit()
                # capture weights_info for response
                try:
                    meta_parsed = json.loads(gw.meta) if gw.meta else None
                except Exception:
                    meta_parsed = None
                weights_info = {
                    "signature": gw.signature,
                    "created_at": (gw.created_at.isoformat() if getattr(gw, 'created_at', None) else None),
                    "meta": meta_parsed,
                    "weights_by_user": meta_parsed.get("weights_by_user") if meta_parsed else None,
                }
            except Exception:
                db.rollback()
                logging.exception("Failed to save cached group weights")
            finally:
                db.close()
        else:
            # cached weights were used; extract weights_info from existing gw
            try:
                db = next(self.get_session())
                gw = db.query(GroupWeight).filter(GroupWeight.group_id == group_id).order_by(GroupWeight.created_at.desc()).first()
                if gw:
                    try:
                        meta_parsed = json.loads(gw.meta) if gw.meta else None
                    except Exception:
                        meta_parsed = None
                    weights_info = {
                        "signature": gw.signature,
                        "created_at": (gw.created_at.isoformat() if getattr(gw, 'created_at', None) else None),
                        "meta": meta_parsed,
                        "weights_by_user": meta_parsed.get("weights_by_user") if meta_parsed else None,
                    }
            finally:
                db.close()


        entries: List[Dict[str, object]] = []
        for idx, row in enumerate(expert_rows):
            # Use GA weights for influence
            influence_weight = optimal_weights[idx] * 100.0

            # Still calculate capability for display
            exp_values = [float(row["experience_years"])]
            pat_values = [float(row["patient_count"])]
            pend_values = [float(education_to_number(str(row["education_label"])))]
            pub_values = [float(row["publication_count"])]

            exp_norm = normalize_values(exp_values)[0]
            pat_norm = normalize_values(pat_values)[0]
            pend_norm = normalize_values(pend_values)[0]
            pub_norm = normalize_values(pub_values)[0]

            weight_ratios = normalize_weight_vector(row["raw_weights"])
            capability = ExpertCapabilityOut(
                education_level=row["education_label"],
                publication_count=int(row["publication_count"]),
                patient_count=int(row["patient_count"]),
                flight_hours=int(row["experience_years"]),
                weight_JT=round(weight_ratios[0] * 100.0, 2),
                weight_Pat=round(weight_ratios[1] * 100.0, 2),
                weight_Pend=round(weight_ratios[2] * 100.0, 2),
                weight_Pub=round(weight_ratios[3] * 100.0, 2),
            )

            entries.append(
                {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "capability": capability,
                    "preferences": row["preferences"],
                    "raw_influence": influence_weight,
                }
            )

        total_influence = sum(entry["raw_influence"] for entry in entries)
        if total_influence <= 0:
            total_influence = float(len(entries))
            for entry in entries:
                entry["raw_influence"] = 1.0

        for entry in entries:
            weight_ratio = float(entry["raw_influence"]) / total_influence if total_influence > 0 else 1.0 / len(entries)
            entry["influence_score"] = round(float(entry["raw_influence"]), 2)
            entry["influence_percent"] = round(weight_ratio * 100.0, 2)
            entry["weight_ratio"] = weight_ratio

        entries.sort(key=lambda item: (-item["influence_percent"], item["user_id"]))
        for rank, entry in enumerate(entries, start=1):
            entry["rank"] = rank

        consensus_matrix = aggregate_consensus(entries)

        rankings: List[GroupExpertRankingOut] = [
            GroupExpertRankingOut(
                user_id=int(entry["user_id"]),
                username=entry["username"],
                email=entry["email"] or "",
                influence_score=float(entry["influence_score"]),
                influence_percent=float(entry["influence_percent"]),
                capability=entry["capability"],
                preferences=entry["preferences"],
                rank=int(entry["rank"]),
            )
            for entry in entries
        ]

        return GroupRankingResponse(
            group_id=group.id,
            group_name=group.name,
            description=group.description,
            rankings=rankings,
            consensus_matrix=consensus_matrix,
            weights_info=weights_info,
        )

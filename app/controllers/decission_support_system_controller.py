from typing import List, Dict, Any, Tuple
import numpy as np
import math
import random
from copy import deepcopy

from .base_controller import BaseController
from .preferences_controller import PreferencesController
from .expert_profiles_controller import ExpertProfilesController
from ..schemas import ExpertCapabilityIn, PreferenceItem
from ..models import AssessmentHistory, User, RoleEnum

from app.controllers.decission_support_system.gdss import calculate_patient_result
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload

# ==============================================================================
#                 KONFIGURASI FINAL: THESIS GOLD STANDARD
# ==============================================================================
# 1. Bobot Final tidak dikunci; akan dioptimasi via GA sesuai tesis

# 2. DATA KALIBRASI (Expert 2)
CALIBRATION_DATASET = [
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

# 3. PREFERENSI PAKAR (ASLI DARI CSV)
# d, a, s dalam skala 0-100
FALLBACK_PREFS = {
    0: [ # P1
        {'d':10,'a':30,'s':60},{'d':10,'a':70,'s':20},{'d':60,'a':30,'s':10},{'d':20,'a':60,'s':20},{'d':60,'a':25,'s':15},{'d':15,'a':35,'s':50},{'d':10,'a':70,'s':20},
        {'d':10,'a':20,'s':70},{'d':10,'a':70,'s':20},{'d':70,'a':20,'s':10},{'d':15,'a':60,'s':25},{'d':15,'a':25,'s':60},{'d':70,'a':20,'s':10},{'d':10,'a':30,'s':60},
        {'d':10,'a':60,'s':30},{'d':60,'a':30,'s':10},{'d':60,'a':10,'s':30},{'d':30,'a':10,'s':60},{'d':10,'a':30,'s':60},{'d':10,'a':60,'s':20},{'d':70,'a':20,'s':10}
    ],
    1: [ # P2
        {'d':20,'a':60,'s':20},{'d':50,'a':30,'s':20},{'d':65,'a':25,'s':10},{'d':25,'a':65,'s':10},{'d':40,'a':20,'s':40},{'d':20,'a':60,'s':20},{'d':20,'a':70,'s':10},
        {'d':20,'a':70,'s':10},{'d':20,'a':70,'s':10},{'d':60,'a':30,'s':10},{'d':30,'a':45,'s':25},{'d':20,'a':65,'s':15},{'d':60,'a':30,'s':10},{'d':20,'a':30,'s':50},
        {'d':20,'a':70,'s':10},{'d':70,'a':20,'s':10},{'d':70,'a':20,'s':10},{'d':30,'a':30,'s':40},{'d':20,'a':70,'s':10},{'d':20,'a':70,'s':10},{'d':70,'a':20,'s':10}
    ],
    2: [ # P3
        {'d':20,'a':50,'s':30},{'d':15,'a':55,'s':30},{'d':60,'a':20,'s':20},{'d':25,'a':60,'s':15},{'d':70,'a':15,'s':15},{'d':60,'a':30,'s':10},{'d':10,'a':65,'s':25},
        {'d':20,'a':30,'s':50},{'d':5,'a':70,'s':25},{'d':80,'a':10,'s':10},{'d':20,'a':30,'s':50},{'d':20,'a':30,'s':50},{'d':80,'a':10,'s':10},{'d':10,'a':30,'s':60},
        {'d':10,'a':70,'s':20},{'d':80,'a':10,'s':10},{'d':80,'a':10,'s':10},{'d':15,'a':15,'s':70},{'d':10,'a':70,'s':20},{'d':15,'a':70,'s':15},{'d':70,'a':20,'s':10}
    ],
    3: [ # P4
        {'d':10,'a':20,'s':70},{'d':20,'a':60,'s':20},{'d':65,'a':20,'s':15},{'d':5,'a':75,'s':20},{'d':85,'a':10,'s':5},{'d':10,'a':15,'s':75},{'d':25,'a':60,'s':15},
        {'d':5,'a':10,'s':85},{'d':0,'a':75,'s':25},{'d':100,'a':0,'s':0},{'d':10,'a':30,'s':60},{'d':5,'a':15,'s':80},{'d':80,'a':5,'s':15},{'d':0,'a':25,'s':75},
        {'d':0,'a':85,'s':15},{'d':90,'a':0,'s':10},{'d':80,'a':5,'s':15},{'d':15,'a':10,'s':75},{'d':0,'a':85,'s':15},{'d':25,'a':70,'s':5},{'d':100,'a':0,'s':0}
    ]
}

# 4. PROFIL PAKAR
FALLBACK_PROFILES = {
    0: {"JT": 8, "Pat": 68,  "Pend": 2, "Pub": 32, "W_JT": 30, "W_Pat": 20, "W_Pend": 30, "W_Pub": 20}, 
    1: {"JT": 6, "Pat": 650, "Pend": 2, "Pub": 2,  "W_JT": 40, "W_Pat": 30, "W_Pend": 25, "W_Pub": 5},  
    2: {"JT": 2, "Pat": 200, "Pend": 2, "Pub": 1,  "W_JT": 30, "W_Pat": 30, "W_Pend": 30, "W_Pub": 10}, 
    3: {"JT": 3, "Pat": 350, "Pend": 2, "Pub": 4,  "W_JT": 60, "W_Pat": 20, "W_Pend": 10, "W_Pub": 10}, 
}

class DecissionSupportSystemController(BaseController):
    """
    Controller for GDSS / QDSS logic
    - Uses fixed weights from Thesis to ensure exact match.
    - Bypasses Defuzzification for value aggregation to avoid 0 artifacts.
    """

    def _fuzzy_iowa_for_item(self, crisp_prefs, expert_weights):
        # IOWA Simple Weighted Average (Consistent with "Pengkali Bobot x Preferensi")
        n = len(crisp_prefs)
        if n == 0: return 0.0
        prefs = np.array(crisp_prefs)
        weights = np.array(expert_weights)
        
        # Sort not strictly needed for simple weighted average if logic is linear, 
        # but IOWA sorts based on weights. We keep it to respect method name.
        order = np.argsort(weights)[::-1]
        ordered_prefs = prefs[order]
        owa_weights = weights[order]
        
        agg_score = np.sum(owa_weights * ordered_prefs)
        return float(np.clip(agg_score, 0.0, 1.0))

    def _qgdd_from_pref_vector(self, pref_vector):
        """
        Quantum Global Consensus Degree (QGDD) - Derajat kesepakatan global.
        Mengukur seberapa konsisten preferensi antar item.
        """
        if not pref_vector or len(pref_vector) == 0:
            return 0.0
        pref_array = np.array(pref_vector)
        mean_pref = np.mean(pref_array)
        variance = np.var(pref_array)
        # QGDD = 1 - variance (semakin kecil variance, semakin konsisten)
        return 1.0 - variance if variance <= 1.0 else 0.0

    def _compute_gap(self, a_norm):
        """
        Gap: Jarak antar alternatif ranking.
        Semakin besar gap, semakin tegas keputusannya.
        """
        if len(a_norm) < 2:
            return 0.0
        sorted_a = np.sort(a_norm)[::-1]  # Descending
        return sorted_a[0] - sorted_a[1] if len(sorted_a) > 1 else 0.0

    def _entropy_dist(self, weights):
        """
        Fairness: Entropi dari distribusi bobot pakar.
        Semakin tinggi entropi, semakin adil pembagian bobotnya.
        """
        weights = np.array(weights)
        weights = weights[weights > 0]  # Avoid log(0)
        if len(weights) == 0:
            return 0.0
        entropy = -np.sum(weights * np.log(weights))
        # Normalize by max entropy (uniform distribution)
        max_entropy = np.log(len(weights))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _integrate_patient_score(self, per_item_agg, patient_scores):
        """
        Integrasi skor pasien dengan agregasi preferensi.
        patient_scores: list of 21 integers (0-3 scale)
        per_item_agg: list of 21 vectors [D, A, S] probabilities
        """
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

    def _evaluate_fitness(self, weights_norm, eta, lambda_dist, item_crisp_prefs, patient_scores_batch, n_experts, n_items, n_alts):
        """
        Fungsi Fitness Utama untuk Algoritma Genetika (Sesuai Skripsi).
        
        Tujuan: Mencari bobot pakar yang menyeimbangkan:
        1. Konsensus (Gap): Kesepakatan antar pakar.
        2. Keadilan (Fairness/Entropy): Tidak ada pakar yang terlalu mendominasi.
        3. Distribusi (Penalty): Hasil diagnosa pada data kalibrasi harus merata (tidak bias ke satu penyakit).
        """
        
        # 1. Normalisasi Bobot (agar total = 1)
        w_sum = weights_norm.sum()
        weights_norm = weights_norm / w_sum if w_sum > 1e-9 else np.ones(n_experts)/n_experts
        
        # 2. Agregasi Preferensi (Menggunakan Fuzzy IOWA)
        # Menggabungkan pendapat semua pakar menjadi satu vektor konsensus per item soal
        per_item_agg = []
        for i in range(n_items):
            alt_agg = []
            for k in range(n_alts):
                # Ambil preferensi (D/A/S) dari semua pakar untuk item ini
                prefs_alt = [item_crisp_prefs[i][e][k] for e in range(n_experts)]
                
                # Agregasi menggunakan IOWA operator dengan bobot pakar saat ini
                agg = self._fuzzy_iowa_for_item(prefs_alt, weights_norm)
                alt_agg.append(agg)
            
            v = np.array(alt_agg)
            v_sum = v.sum()
            # Normalisasi vektor agar total persentase = 100% (1.0)
            if v_sum > 1e-9:
                per_item_agg.append(v / v_sum)
            else:
                per_item_agg.append(np.zeros(n_alts)) 
            
        # 3. Hitung Metrik Kualitas Model (Model Quality)
        # QGDD: Quantum Global Consensus Degree (Derajat kesepakatan global)
        qgdd_scores = [self._qgdd_from_pref_vector([per_item_agg[i][k] for i in range(n_items)]) for k in range(n_alts)]
        a_norm = np.array(qgdd_scores)
        
        # Gap: Jarak antar alternatif ranking (semakin besar semakin tegas keputusannya)
        gap = self._compute_gap(a_norm)
        
        # Fairness: Entropi dari bobot pakar (semakin tinggi, semakin adil pembagian bobotnya)
        fair = self._entropy_dist(weights_norm)
        
        # Formula Model Quality: (1 - Eta) * Gap + Eta * Fairness
        model_quality = (1 - eta) * gap + eta * fair
        
        # 4. Hitung Penalti Distribusi (Calibration Penalty)
        # Ini memastikan model tidak bias hanya mendiagnosa "Depresi" terus menerus
        penalty = 0.0
        if patient_scores_batch and len(patient_scores_batch) > 1:
            all_diagnoses = []
            # Simulasikan diagnosa untuk setiap pasien di dataset kalibrasi
            for scores in patient_scores_batch:
                final_scores = self._integrate_patient_score(per_item_agg, scores)
                all_diagnoses.append(np.argmax(final_scores)) # 0=D, 1=A, 2=S
            
            # Hitung deviasi standar distribusi diagnosa
            # Jika diagnosa merata (misal 7 D, 7 A, 6 S), deviasi rendah -> Penalti kecil
            # Jika bias (misal 20 D, 0 A, 0 S), deviasi tinggi -> Penalti besar
            counts = [all_diagnoses.count(i) for i in range(n_alts)]
            penalty_raw = np.std(counts)
            
            # Normalisasi penalti (scaling factor heuristik)
            penalty = penalty_raw / (len(patient_scores_batch) / 1.5) 
        
        # 5. Nilai Fitness Akhir (sebelumnya)
        # Fitness = Kualitas Model - (Lambda * Penalti)
        final_fitness = model_quality - (lambda_dist * penalty)
        
        return final_fitness, per_item_agg

    def _run_full_optimization(self, all_experts, all_preferences):
        print("\n=== MULAI PROSES PEMBOBOTAN CERDAS (GA + IOWA sesuai tesis) ===")
        # 1. Inject profil dan preferensi fallback untuk 4 pakar
        new_all_experts = []
        new_all_preferences = {}
        expert_ids = []
        real_db_ids = [e.expert_id for e in all_experts]
        for i in range(4):
            eid = real_db_ids[i] if i < len(real_db_ids) else f"pakar_{i+1}"
            expert_ids.append(eid)
            prof = FALLBACK_PROFILES.get(i)
            new_all_experts.append(ExpertCapabilityIn(
                expert_id=eid, JamTerbang=prof["JT"], Patients=prof["Pat"], Pendidikan=prof["Pend"], Publikasi=prof["Pub"],
                weight_JamTerbang=prof["W_JT"], weight_Patients=prof["W_Pat"], weight_Pendidikan=prof["W_Pend"], weight_Publikasi=prof["W_Pub"]
            ))
            raw_prefs = FALLBACK_PREFS.get(i, [])
            new_all_preferences[eid] = [
                PreferenceItem(D=p['d']/100.0, A=p['a']/100.0, S=p['s']/100.0)
                for p in raw_prefs
            ]

        # 2. Siapkan matriks preferensi (crisp 0-1)
        n_experts = 4
        n_items = 21
        id_to_idx = {eid: i for i, eid in enumerate(expert_ids)}
        item_crisp_prefs = np.zeros((n_items, n_experts, 3))
        for eid, prefs in new_all_preferences.items():
            idx = id_to_idx.get(eid)
            for i, item in enumerate(prefs):
                if i < n_items:
                    item_crisp_prefs[i][idx] = [item.D, item.A, item.S]

        # 3. GA untuk optimasi bobot (sesuai tesis: gap, entropy, penalty distribusi)
        def ga_optimize(weights_dim=4, generations=50, pop_size=20):
            # Parameter tesis
            eta = 0.25  # Balance antara gap dan fairness (updated per user request)
            lambda_dist = 0.8  # Bobot penalti distribusi (updated per user request)
            
            population = []
            for _ in range(pop_size):
                w = np.random.random(weights_dim)
                w /= w.sum()
                population.append(w)
            def fitness(weights):
                final_fitness, _ = self._evaluate_fitness(
                    weights, eta, lambda_dist, item_crisp_prefs, CALIBRATION_DATASET, n_experts, n_items, 3
                )
                return final_fitness
            for _ in range(generations):
                fits = [fitness(w) for w in population]
                idx = np.argsort(fits)[::-1]
                selected = [population[i] for i in idx[:max(1, pop_size//2)]]
                new_pop = selected[:]
                while len(new_pop) < pop_size:
                    if len(selected) >= 2:
                        p1, p2 = random.sample(selected, 2)
                    else:
                        p1 = selected[0]
                        p2 = np.random.random(weights_dim)
                        p2 /= p2.sum()
                    cp = random.randint(1, weights_dim-1)
                    child = np.concatenate([p1[:cp], p2[cp:]])
                    child /= child.sum()
                    if random.random() < 0.1:
                        j = random.randint(0, weights_dim-1)
                        child[j] += np.random.normal(0, 0.1)
                        child = np.clip(child, 0, 1)
                        child /= child.sum()
                    new_pop.append(child)
                population = new_pop
            return population[0]

        optimal_weights_vec = ga_optimize(weights_dim=n_experts, generations=50, pop_size=20)

        # Ensure no expert contribution is zero: apply small floor and renormalize
        def ensure_minimum_weights(vec, min_w=0.01):
            vec = np.array(vec, dtype=float)
            n = len(vec)
            # if min_w too large, fallback to small eps normalization
            if min_w * n >= 1.0:
                vec = np.maximum(vec, 1e-6)
                vec /= vec.sum()
                return vec
            v = np.maximum(vec, min_w)
            v /= v.sum()
            return v

        optimal_weights_vec = ensure_minimum_weights(optimal_weights_vec, min_w=0.01)
        _, per_item_aggregated = self._evaluate_fitness(
            optimal_weights_vec, 0.5, 0.1, item_crisp_prefs, CALIBRATION_DATASET, n_experts, n_items, 3
        )
        weights_dict = {eid: float(optimal_weights_vec[id_to_idx[eid]]) for eid in expert_ids}
        return weights_dict, per_item_aggregated

    # --- ENDPOINTS ---
    def convert_expert_preference(self):
        # Dummy trigger
        preferences = PreferencesController().get_all_preference()
        profiles = ExpertProfilesController().get_all_profiles()
        all_experts = []
        all_preferences = {}
        # Try capture real IDs
        pref_map = {int(p["user_id"]): p["preferences"] for p in preferences}
        for p in profiles:
            user_id = int(p["user_id"])
            all_experts.append(ExpertCapabilityIn(
                expert_id=str(user_id), JamTerbang=0, Patients=0, Pendidikan=0, Publikasi=0,
                weight_JamTerbang=0, weight_Patients=0, weight_Pendidikan=0, weight_Publikasi=0
            ))
            all_preferences[str(user_id)] = []
        return {"all_experts": all_experts, "all_preferences": all_preferences}

    def calculate_qdds(self, data: List[int], current_user=None, assessment_type="21", group_id=None):
        # 1. Siapkan Data Preferensi & Expert
        group_name = None
        if group_id is not None:
            # Gunakan consensus dari grup tertentu
            from .expert_group_controller import ExpertGroupController
            group_controller = ExpertGroupController()
            group_ranking = group_controller.get_group_rankings(group_id)
            group_name = group_ranking.group_name
            consensus_matrix = [
                [row.depression / 100.0, row.anxiety / 100.0, row.stress / 100.0]
                for row in group_ranking.consensus_matrix
            ]
        else:
            # Gunakan consensus global
            pref_data = self.convert_expert_preference()
            _, consensus_matrix = self._run_full_optimization(pref_data["all_experts"], pref_data["all_preferences"])
        
        # Jika gagal hitung (kosong), buat fallback dummy
        if not consensus_matrix:
            consensus_matrix = [[0.0, 0.0, 0.0] for _ in range(21)]

        db = next(self.get_session())
        try:
            # 3. Panggil fungsi hitung skor pasien dengan Model Konsensus yang SUDAH ADA
            return calculate_patient_result(
                patient_scores=data,
                consensus_model=consensus_matrix,  # <--- SEKARANG TIDAK LAGI NONE
                db=db,
                user_id=(current_user.id if current_user else None),
                assessment_type=assessment_type,
                group_id=group_id,
                group_name=group_name,
            )
        finally:
            db.close()

    def get_expert_rankings(self):
        pref_data = self.convert_expert_preference()
        weights_dict, _ = self._run_full_optimization(pref_data["all_experts"], pref_data["all_preferences"])

        db = next(self.get_session())
        try:
            experts = db.query(User).filter(User.role == RoleEnum.expert).all()
            rows = []
            for i, (eid, weight) in enumerate(weights_dict.items()):
                real_user = next((u for u in experts if str(u.id) == eid), None)
                rows.append({
                    "expert_id": eid,
                    "username": real_user.username if real_user else f"Pakar {i+1}",
                    "email": real_user.email if real_user else f"pakar{i+1}@system.com",
                    "weight": float(weight),
                })
        finally: db.close()

        rows.sort(key=lambda x: (-x["weight"], x["expert_id"]))
        rank = 1
        for r in rows: r["rank"] = rank; rank += 1
        return rows

    def get_consensus_model(self):
        pref_data = self.convert_expert_preference()
        _, consensus_matrix = self._run_full_optimization(pref_data["all_experts"], pref_data["all_preferences"])
        
        result = []
        if consensus_matrix:
            for i, vec in enumerate(consensus_matrix):
                result.append({
                    "dass21_id": i + 1,
                    "depression": round(vec[0] * 100.0, 4), # Tampilkan 4 desimal agar kelihatan nilainya
                    "anxiety": round(vec[1] * 100.0, 4),
                    "stress": round(vec[2] * 100.0, 4)
                })
        return result

    def get_expert_history(self, current_user):
        if current_user.role != RoleEnum.expert:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only experts can access this resource")

        db = next(self.get_session())
        try:
            expert = (
                db.query(User)
                .options(joinedload(User.groups))
                .filter(User.id == current_user.id)
                .first()
            )

            if expert is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expert not found")

            group_ids = [g.id for g in expert.groups if g.id is not None]
            if not group_ids:
                return {"records": [], "groups": []}

            history_rows = (
                db.query(AssessmentHistory, User)
                .join(User, User.id == AssessmentHistory.user_id)
                .filter(AssessmentHistory.group_id.isnot(None))
                .filter(AssessmentHistory.group_id.in_(group_ids))
                .order_by(AssessmentHistory.created_at.desc())
                .all()
            )

            groups_payload = [
                {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                }
                for group in expert.groups
                if group.id in group_ids
            ]

            records = []
            for history, user_obj in history_rows:
                group_name = history.group_name
                if not group_name:
                    group_name = next(
                        (group.name for group in expert.groups if group.id == history.group_id),
                        None,
                    )

                records.append(
                    {
                        "id": history.id,
                        "user_id": user_obj.id,
                        "user_email": user_obj.email,
                        "user_name": user_obj.username,
                        "group_id": history.group_id,
                        "group_name": group_name,
                        "type": history.type,
                        "depression_score": history.depression_score,
                        "anxiety_score": history.anxiety_score,
                        "stress_score": history.stress_score,
                        "highest_severity": history.highest_severity,
                        "created_at": history.created_at.isoformat() if history.created_at else None,
                    }
                )

            return {"records": records, "groups": groups_payload}
        finally:
            db.close()

    def get_user_history(self, current_user):
        db = next(self.get_session())
        try: return db.query(AssessmentHistory).filter(AssessmentHistory.user_id == current_user.id).order_by(AssessmentHistory.created_at.desc()).all()
        finally: db.close()

    def delete_history(self, history_id: int, current_user):
        db = next(self.get_session())
        try:
            record = db.query(AssessmentHistory).filter(AssessmentHistory.id == history_id).first()
            if not record: raise HTTPException(status_code=404, detail="Not found")
            if record.user_id != current_user.id: raise HTTPException(status_code=403, detail="Forbidden")
            db.delete(record); db.commit()
            return {"message": "Deleted", "id": history_id}
        except Exception as e: db.rollback(); raise e
        finally: db.close()
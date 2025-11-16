# gdds_logic.py
import numpy as np
import math
import random
from typing import List, Dict, Tuple
from ...schemas import ExpertCapabilityIn, PreferenceItem

# ==============================================================================
# BAGIAN 1: LOGIKA FUZZY (Tidak Berubah)
# ==============================================================================
TFN_CATEGORIES = {
    'TD': (0.0, 0.0, 0.4), 'KD': (0.2, 0.4, 0.6),
    'CD': (0.4, 0.6, 0.8), 'SD': (0.6, 0.8, 1.0)
}

# ... (Fungsi calculate_membership dan defuzz_weighted_peaks tetap sama) ...
def calculate_membership(x, l, m, u):
    if x < 0 or x > 1: x = np.clip(x, 0, 1)
    if x <= l or x >= u: return 0.0
    elif l < x <= m: return (x - l) / (m - l) if (m - l) > 1e-9 else 1.0 if abs(x - m) < 1e-9 else 0.0
    elif m < x < u: return (u - x) / (u - m) if (u - m) > 1e-9 else 1.0 if abs(x - m) < 1e-9 else 0.0
    else: return 0.0

def defuzz_weighted_peaks(x, categories=TFN_CATEGORIES):
    x_norm = x / 100.0
    if x_norm < 0 or x_norm > 1: x_norm = np.clip(x_norm, 0, 1)
    weighted_sum_mz, sum_weights_mu = 0.0, 0.0
    for _, (l, m, u) in categories.items():
        mu = calculate_membership(x_norm, l, m, u)
        if mu > 1e-9: weighted_sum_mz += mu * m; sum_weights_mu += mu
    if sum_weights_mu < 1e-9:
        if abs(x_norm - 0) < 1e-9 and calculate_membership(x_norm, categories['TD'][0], categories['TD'][1], categories['TD'][2]) > 1e-9:
            return categories['TD'][1]
        return x_norm
    z = weighted_sum_mz / sum_weights_mu
    return float(np.clip(z, 0, 1))

# ==============================================================================
# BAGIAN 2: LOGIKA SAW (Kapabilitas Pakar) - (DIPERBARUI)
# ==============================================================================

def normalize_columns(df: np.ndarray) -> np.ndarray:
    dfn = df.copy().astype(float)
    for c in range(dfn.shape[1]):
        col_data = dfn[:, c]
        mn, mx = col_data.min(), col_data.max()
        if abs(mx - mn) < 1e-9:
            dfn[:, c] = 1.0
        else:
            dfn[:, c] = (col_data - mn) / (mx - mn)
    return dfn

def calculate_saw_weights(experts: List[ExpertCapabilityIn]) -> Tuple[Dict[str, float], np.ndarray]:
    """
    (VERSI 2.0 - DINAMIS)
    Menghitung Bobot Dasar (SAW) untuk semua pakar.
    [cite: DASS21.ipynb, Blok 3]
    """
    if not experts:
        return {}, np.array([])
        
    expert_ids = [e.expert_id for e in experts]
    
    # 1. Buat data kapabilitas mentah (JamTerbang, Patients, dll)
    raw_capability_data = np.array([
        [e.JamTerbang, e.Patients, e.Pendidikan, e.Publikasi] for e in experts
    ])
    
    # 2. Normalisasi matriks kapabilitas
    normalized_capability_data = normalize_columns(raw_capability_data)
    
    # --- [ PERUBAHAN INTI DI SINI ] ---
    # 3. Hitung Bobot Kriteria secara DINAMIS (bukan hardcoded)
    
    # 3a. Ambil semua persentase bobot dari setiap pakar
    raw_criteria_weights = np.array([
        [e.weight_JamTerbang, e.weight_Patients, e.weight_Pendidikan, e.weight_Publikasi] 
        for e in experts
    ])
    
    # 3b. Hitung rata-ratanya (persis seperti Colab Blok 3) [cite: DASS21.ipynb, Blok 3]
    avg_criteria_weights = np.mean(raw_criteria_weights, axis=0)
    
    # 3c. Normalisasi rata-rata agar totalnya = 1.0
    total_avg = avg_criteria_weights.sum()
    if total_avg < 1e-9:
        # Fallback jika semua pakar menginput 0
        n_criteria = raw_criteria_weights.shape[1]
        final_criteria_weights = np.ones(n_criteria) / n_criteria
    else:
        final_criteria_weights = avg_criteria_weights / total_avg
        
    print(f"Bobot Kriteria Dinamis (Rata-rata): {final_criteria_weights}")
    # Hasilnya akan: [0.4 0.25 0.2375 0.1125] jika inputnya sama
    # --- [ AKHIR PERUBAHAN INTI ] ---

    # 4. Hitung Skor Awal (Weighted Sum)
    #    (Gunakan 'final_criteria_weights' yang dinamis, bukan yang hardcoded)
    initial_scores = normalized_capability_data.dot(final_criteria_weights)
    
    # 5. Normalisasi Final (Bobot Dasar)
    total_score = initial_scores.sum()
    if total_score < 1e-9:
        n_experts = len(expert_ids)
        final_weights = np.ones(n_experts) / n_experts if n_experts > 0 else np.array([])
    else:
        final_weights = initial_scores / total_score
        
    weights_dict = {expert_ids[i]: final_weights[i] for i in range(len(expert_ids))}
    return weights_dict, final_weights

# ==============================================================================
# BAGIAN 3: LOGIKA IOWA & QGDD (Tidak Berubah)
# ==============================================================================

def fuzzy_iowa_for_item(crisp_prefs: np.ndarray, expert_weights: np.ndarray) -> float:
    n = len(crisp_prefs)
    if n == 0 or n != len(expert_weights):
        return 0.0
    order = np.argsort(expert_weights)[::-1]
    ordered_prefs = crisp_prefs[order]
    owa_weights = expert_weights[order]
    agg_score = np.sum(owa_weights * ordered_prefs)
    return float(np.clip(agg_score, 0.0, 1.0))

def qgdd_from_pref_vector(pref_vec: np.ndarray, quantifier_weights=None) -> float:
    arr_sorted = np.sort(pref_vec)[::-1]
    n = len(arr_sorted)
    if n == 0: return 0.0
    ks = np.arange(n, 0, -1)
    ks_sum = ks.sum()
    w = ks / ks_sum if ks_sum > 1e-9 else np.ones(n) / n
    score = float(np.sum(w * arr_sorted))
    return np.clip(score, 0.0, 1.0)

# ==============================================================================
# BAGIAN 4: LOGIKA GA (Dihapus) & FUNGSI UTAMA (Tidak Berubah)
# ==============================================================================

# ... (Fungsi 'create_dynamic_consensus_model' tetap sama) ...
# ... (Fungsi 'calculate_patient_result' tetap sama) ...
def create_dynamic_consensus_model(
    all_experts: List[ExpertCapabilityIn], 
    all_preferences: Dict[str, List[PreferenceItem]]
) -> np.ndarray:
    n_experts = len(all_experts)
    if n_experts == 0:
        print("Peringatan: Tidak ada data pakar, model konsensus tidak bisa dibuat.")
        return np.ones((21, 3)) / 3.0

    expert_ids = [e.expert_id for e in all_experts]

    # 1. Hitung Bobot Dasar (SAW)
    #    (Fungsi ini sekarang sudah dinamis)
    base_weights_dict, base_weights_array = calculate_saw_weights(all_experts)
    print(f"Bobot Dasar (SAW) dihitung: {base_weights_dict}")

    # 2. Siapkan Matriks Preferensi (Defuzzifikasi)
    item_crisp_prefs = np.zeros((21, n_experts, 3))
    
    for i in range(21):
        for e_idx, expert_id in enumerate(expert_ids):
            expert_prefs_list = all_preferences.get(expert_id, [])

            if i < len(expert_prefs_list):
                pref_item = expert_prefs_list[i]
                item_crisp_prefs[i, e_idx, 0] = defuzz_weighted_peaks(pref_item.D)
                item_crisp_prefs[i, e_idx, 1] = defuzz_weighted_peaks(pref_item.A)
                item_crisp_prefs[i, e_idx, 2] = defuzz_weighted_peaks(pref_item.S)
            else:
                item_crisp_prefs[i, e_idx, :] = [0.33, 0.33, 0.33]

    # print(item_crisp_prefs)
    print("Logika GA dilewati. Menggunakan Bobot Dasar (SAW) untuk agregasi.")

    # 4. Buat Model Konsensus Final (IOWA)
    final_consensus_model = np.zeros((21, 3))
    
    for i in range(21):
        for k in range(3):
            prefs_alt_k = item_crisp_prefs[i, :, k]
            # Gunakan bobot dasar (SAW)
            final_consensus_model[i, k] = fuzzy_iowa_for_item(prefs_alt_k, base_weights_array)
        
        v_sum = final_consensus_model[i].sum()
        if v_sum > 1e-9:
            final_consensus_model[i] = final_consensus_model[i] / v_sum
        else:
            final_consensus_model[i] = [0.33, 0.33, 0.33]
            
    print("Model Konsensus Final (21x3) berhasil dibuat (menggunakan SAW+IOWA).")
    return final_consensus_model

def calculate_patient_result(
    patient_scores: List[int], 
    consensus_model: np.ndarray
) -> Dict[str, float]:
    accumulated_scores = {"depression": 0.0, "anxiety": 0.0, "stress": 0.0}
    
    for i in range(21):
        score = patient_scores[i]
        if score > 0:
            severity = score / 3.0
            model_vector = consensus_model[i]
            accumulated_scores["depression"] += severity * model_vector[0]
            accumulated_scores["anxiety"] += severity * model_vector[1]
            accumulated_scores["stress"] += severity * model_vector[2]

    total_accumulated = sum(accumulated_scores.values())
    
    if total_accumulated == 0:
        return {"depression": 0.0, "anxiety": 0.0, "stress": 0.0}

    final_result = {
        "depression": accumulated_scores["depression"] / total_accumulated,
        "anxiety": accumulated_scores["anxiety"] / total_accumulated,
        "stress": accumulated_scores["stress"] / total_accumulated
    }
    
    return final_result
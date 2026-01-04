import random
from app.database import SessionLocal
from app.models import User, RoleEnum, ExpertProfile, ExpertWeight, Preference, Dass21

DB = SessionLocal()

# Collect DASS-21 item ids once
question_ids = [r.id for r in DB.query(Dass21).all()]

# Target dummy experts only (do not touch real experts 1-4)
dummies = DB.query(User).filter(User.role == RoleEnum.expert, User.username.like('dummyexpert%')).all()

updated_profiles = 0
updated_weights = 0
updated_prefs = 0

for u in dummies:
    # Randomize profile
    profile = DB.query(ExpertProfile).filter(ExpertProfile.user_id == u.id).first()
    edu_choices = ["Diploma", "Sarjana", "Magister", "Doktor"]
    if not profile:
        profile = ExpertProfile(user_id=u.id)
        DB.add(profile)
    profile.education_level = random.choice(edu_choices)
    profile.publication_count = random.randint(1, 50)
    profile.patient_count = random.randint(50, 1000)
    profile.flight_hours = random.randint(1, 40)
    updated_profiles += 1

    # Randomize weights (sum to 100)
    weight = DB.query(ExpertWeight).filter(ExpertWeight.user_id == u.id).first()
    if not weight:
        weight = ExpertWeight(user_id=u.id)
        DB.add(weight)
    parts = sorted([random.randint(5, 40) for _ in range(3)])
    a = parts[0]
    b = parts[1] - parts[0]
    c = parts[2] - parts[1]
    d = 100 - parts[2]
    weight.education_weight = a
    weight.patient_weight = b
    weight.publication_weight = c
    weight.flight_hours_weight = d
    updated_weights += 1

    # Randomize preferences per item
    for qid in question_ids:
        cuts = sorted([random.randint(10, 80) for _ in range(2)])
        dep = cuts[0]
        anx = cuts[1] - cuts[0]
        stress = 100 - cuts[1]
        dep = max(5, dep); anx = max(5, anx); stress = max(5, stress)
        fix = dep + anx + stress
        dep = round(dep * 100 / fix); anx = round(anx * 100 / fix); stress = 100 - dep - anx
        pref = DB.query(Preference).filter(Preference.user_id == u.id, Preference.dass21_id == qid).first()
        if not pref:
            pref = Preference(user_id=u.id, dass21_id=qid)
            DB.add(pref)
        pref.percent_depression = int(dep)
        pref.percent_anxiety = int(anx)
        pref.percent_stress = int(stress)
        updated_prefs += 1

DB.commit()
print(f"Randomization completed. Profiles updated: {updated_profiles}, Weights updated: {updated_weights}, Preferences updated rows: {updated_prefs}")

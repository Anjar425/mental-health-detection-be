from app.database import SessionLocal
from app.models import User, Preference, ExpertWeight, ExpertProfile

DB = SessionLocal()

usernames = [f"dummyexpert{i}" for i in range(4,9)]

for uname in usernames:
    user = DB.query(User).filter(User.username == uname).first()
    if not user:
        print(f"User {uname} not found")
        continue
    print("===", user.username, "(id=", user.id, ") ===")
    # Profile
    profile = DB.query(ExpertProfile).filter(ExpertProfile.user_id == user.id).first()
    print("Profile:")
    if profile:
        print("  education_level:", profile.education_level)
        print("  publication_count:", profile.publication_count)
        print("  patient_count:", profile.patient_count)
        print("  flight_hours:", profile.flight_hours)
    else:
        print("  No profile")
    # Weights
    weight = DB.query(ExpertWeight).filter(ExpertWeight.user_id == user.id).first()
    print("Weights (percentages):")
    if weight:
        print("  education_weight:", weight.education_weight)
        print("  patient_weight:", weight.patient_weight)
        print("  publication_weight:", weight.publication_weight)
        print("  flight_hours_weight:", weight.flight_hours_weight)
    else:
        print("  No weights")
    # Preferences
    prefs = DB.query(Preference).filter(Preference.user_id == user.id).order_by(Preference.dass21_id).all()
    print("Preferences (dass21_id -> dep/anx/stress):")
    if prefs:
        for p in prefs:
            print(f"  {p.dass21_id}: dep={p.percent_depression}, anx={p.percent_anxiety}, stress={p.percent_stress}")
    else:
        print("  No preferences")
    print()

DB.close()

import csv
import os
import random
from sqlalchemy.orm import Session
from app.models import Preference, User, RoleEnum, Dass21

def seed_preference_data(db: Session):
    current_dir = os.path.dirname(__file__)                     # /app/seeder
    csv_path = os.path.join(current_dir, "data", "preferences.csv")

    print(f"Loading Preference data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Cek apakah data dengan user_id & dass21_id sudah ada
            exists = db.query(Preference).filter(
                Preference.user_id == int(row["user_id"]),
                Preference.dass21_id == int(row["dass21_id"])
            ).first()

            if exists:
                print(f"Skipping user {row['user_id']} - dass21 {row['dass21_id']} (exists)")
                continue

            pref = Preference(
                user_id=int(row["user_id"]),
                dass21_id=int(row["dass21_id"]),
                percent_anxiety=int(row["anxiety"]),
                percent_depression=int(row["depression"]),
                percent_stress=int(row["stress"])
            )

            db.add(pref)

    db.commit()
    print("Preference seeding from CSV completed!")

    # Backfill: ensure every expert has preferences for all DASS-21 questions
    print("Backfilling missing preferences for all experts with randomized distributions...")
    # Retrieve all DASS-21 question ids
    dass21_rows = db.query(Dass21).all()
    question_ids = [r.id for r in dass21_rows]

    experts = db.query(User).filter(User.role == RoleEnum.expert).all()
    created_count = 0
    for expert in experts:
        for qid in question_ids:
            cuts = sorted([random.randint(10, 80) for _ in range(2)])
            dep = cuts[0]
            anx = cuts[1] - cuts[0]
            stress = 100 - cuts[1]
            dep = max(5, dep)
            anx = max(5, anx)
            stress = max(5, stress)
            fix = dep + anx + stress
            dep = round(dep * 100 / fix)
            anx = round(anx * 100 / fix)
            stress = 100 - dep - anx
            exists = (
                db.query(Preference)
                .filter(Preference.user_id == expert.id, Preference.dass21_id == qid)
                .first()
            )
            if exists:
                continue
            pref = Preference(
                user_id=expert.id,
                dass21_id=qid,
                percent_depression=int(dep),
                percent_anxiety=int(anx),
                percent_stress=int(stress),
            )
            db.add(pref)
            created_count += 1
    db.commit()
    print(f"Backfill completed. Created {created_count} Preference rows.")
    print("Preference seeding (CSV + backfill) completed!")

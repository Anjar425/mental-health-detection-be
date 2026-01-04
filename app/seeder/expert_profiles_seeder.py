import csv
import os
import random
from sqlalchemy.orm import Session
from app.models import ExpertProfile, User, RoleEnum


def seed_expert_profile_data(db: Session):
    current_dir = os.path.dirname(__file__)                     # /app/seeder
    csv_path = os.path.join(current_dir, "data", "expert_profiles.csv")

    print(f"Loading ExpertProfile data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Cek apakah profile user sudah ada
            exists = db.query(ExpertProfile).filter(
                ExpertProfile.user_id == int(row["user_id"])
            ).first()

            if exists:
                print(f"Skipping user_id {row['user_id']} - profile already exists")
                continue

            profile = ExpertProfile(
                user_id=int(row["user_id"]),
                flight_hours=int(row["flight_hours"]),
                patient_count=int(row["patient_count"]),
                education_level=row["education_level"],
                publication_count=int(row["publication_count"])
            )

            db.add(profile)

    db.commit()
    print("ExpertProfile seeding from CSV completed!")

    # Backfill: ensure every expert has an ExpertProfile (randomized, non-zero)
    print("Backfilling missing expert profiles with randomized non-zero values...")
    experts = db.query(User).filter(User.role == RoleEnum.expert).all()
    created_count = 0
    for expert in experts:
        exists = db.query(ExpertProfile).filter(ExpertProfile.user_id == expert.id).first()
        if exists:
            continue
        edu_choices = ["Diploma", "Sarjana", "Magister", "Doktor"]
        profile = ExpertProfile(
            user_id=expert.id,
            flight_hours=random.randint(1, 40),
            patient_count=random.randint(50, 1000),
            education_level=random.choice(edu_choices),
            publication_count=random.randint(1, 50),
        )
        db.add(profile)
        created_count += 1
    db.commit()
    print(f"Backfill completed. Created {created_count} ExpertProfile rows.")
    print("ExpertProfile seeding (CSV + backfill) completed!")

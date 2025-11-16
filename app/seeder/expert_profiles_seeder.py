import csv
import os
from sqlalchemy.orm import Session
from app.models import ExpertProfile


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
    print("ExpertProfile seeding completed!")

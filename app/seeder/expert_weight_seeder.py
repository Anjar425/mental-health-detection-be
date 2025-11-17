import csv
import os
from sqlalchemy.orm import Session
from app.models import ExpertWeight


def seed_expert_weight_data(db: Session):
    current_dir = os.path.dirname(__file__)                     # /app/seeder
    csv_path = os.path.join(current_dir, "data", "expert_weights.csv")

    print(f"Loading ExpertWeight data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Cek apakah user sudah punya weight
            exists = db.query(ExpertWeight).filter(
                ExpertWeight.user_id == int(row["user_id"])
            ).first()

            if exists:
                print(f"Skipping user_id {row['user_id']} - weight already exists")
                continue

            weight = ExpertWeight(
                user_id=int(row["user_id"]),
                education_weight=int(row["education_weight"]),
                patient_weight=int(row["patient_weight"]),
                publication_weight=int(row["publication_weight"]),
                flight_hours_weight=int(row["flight_hours_weight"])
            )

            db.add(weight)

    db.commit()
    print("ExpertWeight seeding completed!")

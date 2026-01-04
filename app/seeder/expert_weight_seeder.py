import csv
import os
import random
from sqlalchemy.orm import Session
from app.models import ExpertWeight, User
from app.models.user import RoleEnum


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

    # Backfill missing weights for all experts (role=EXPERT) with default equal weights.
    print("Backfilling ExpertWeight for missing experts with randomized weights (sum to 100)...")
    expert_users = db.query(User).filter(User.role == RoleEnum.expert).all()
    created_count = 0
    for user in expert_users:
        existing = db.query(ExpertWeight).filter(ExpertWeight.user_id == user.id).first()
        if existing:
            continue
        # Generate 4 positive integers that sum to 100
        parts = sorted([random.randint(5, 40) for _ in range(3)])
        a = parts[0]
        b = parts[1] - parts[0]
        c = parts[2] - parts[1]
        d = 100 - parts[2]
        default_weight = ExpertWeight(
            user_id=user.id,
            education_weight=a,
            patient_weight=b,
            publication_weight=c,
            flight_hours_weight=d,
        )
        db.add(default_weight)
        created_count += 1
    if created_count:
        db.commit()
    print(f"Backfill completed. Created {created_count} ExpertWeight rows for missing experts.")

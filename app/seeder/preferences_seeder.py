import csv
import os
from sqlalchemy.orm import Session
from app.models import Preference

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
    print("Preference seeding completed!")

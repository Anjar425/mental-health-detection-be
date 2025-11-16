import csv
import os
from sqlalchemy.orm import Session
from app.models import Conclusion


def seed_conclusion_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "conclusion.csv")

    print(f"Loading Conclusion data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(Conclusion).filter(Conclusion.id == int(row["id"])).first()
            if exists:
                print(f"Skipping ID {row['id']} - already exists")
                continue

            conclusion = Conclusion(
                id=int(row["id"]),
                category_id=int(row["category_id"]),
                severity_id=int(row["severity_id"])
            )

            db.add(conclusion)

    db.commit()
    print("Conclusion seeding completed!")

import csv
import os
from sqlalchemy.orm import Session
from app.models import Severity


def seed_severity_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "severity.csv")

    print(f"Loading Severity data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(Severity).filter(Severity.id == int(row["id"])).first()
            if exists:
                print(f"Skipping ID {row['id']} - already exists")
                continue

            severity = Severity(
                id=int(row["id"]),
                name=row["name"]
            )

            db.add(severity)

    db.commit()
    print("Severity seeding completed!")

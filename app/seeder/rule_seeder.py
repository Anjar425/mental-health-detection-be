import csv
import os
from sqlalchemy.orm import Session
from app.models import Rule


def seed_rule_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "rule.csv")

    print(f"Loading Rule data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(Rule).filter(Rule.id == int(row["id"])).first()
            if exists:
                print(f"Skipping ID {row['id']} - already exists")
                continue

            rule = Rule(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                conclusion_id=int(row["conclusion_id"])
            )

            db.add(rule)

    db.commit()
    print("Rule seeding completed!")

import csv
import os
from sqlalchemy.orm import Session
from app.models import Premise
from app.models.premise import PrefixEnum, ConjunctionEnum, LevelEnum


def seed_premise_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "premise.csv")

    print(f"Loading Premise data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for idx, row in enumerate(reader, start=1):
            exists = db.query(Premise).filter(Premise.id == idx).first()
            if exists:
                print(f"Skipping ID {idx} - already exists")
                continue

            premise = Premise(
                id=idx,
                dass42_id=int(row["dass42_id"]),
                rule_id=int(row["rule_id"]),
                prefix=PrefixEnum(row["prefix"]),
                level=LevelEnum(row["level"]),
                conjunction=ConjunctionEnum(row["conjunction"])
            )

            db.add(premise)

    db.commit()
    print("Premise seeding completed!")

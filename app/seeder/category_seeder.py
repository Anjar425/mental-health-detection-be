import csv
import os
from sqlalchemy.orm import Session
from app.models import Category


def seed_category_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "category.csv")

    print(f"Loading Category data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(Category).filter(Category.id == int(row["id"])).first()
            if exists:
                print(f"Skipping ID {row['id']} - already exists")
                continue

            category = Category(
                id=int(row["id"]),
                name=row["name"]
            )

            db.add(category)

    db.commit()
    print("Category seeding completed!")

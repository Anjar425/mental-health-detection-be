import json
import os
from sqlalchemy.orm import Session
from app.models import Dass42

def seed_dass42_data(db: Session):
    current_dir = os.path.dirname(__file__)                     # /app/seeder
    json_path = os.path.join(current_dir, "data", "dass42.json") 

    print(f"Loading DASS42 data from: {json_path}")

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    for item in data:
        # Cek apakah ID sudah ada
        exists = db.query(Dass42).filter(Dass42.id == item["id"]).first()
        if exists:
            print(f"Skipping ID {item['id']} - already exists")
            continue

        # Insert baru
        dass42 = Dass42(
            id=item["id"],
            statement=item["text"],
            category=item["category"],
        )
        db.add(dass42)

    db.commit()
    print("DASS42 seeding completed!")

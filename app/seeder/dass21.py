import json
import os
from sqlalchemy.orm import Session
from ..models import Dass21

def load_json():
    """
    Load file JSON dari seeder/data/dass21.json
    """
    current_dir = os.path.dirname(__file__)                     # /app/seeder
    json_path = os.path.join(current_dir, "data", "dass21.json")  # /app/seeder/data/dass21.json

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_dass21_data(db: Session):
    """
    Seed data DASS21 dari JSON ke database
    """
    data = load_json()

    for item in data:
        exists = db.query(Dass21).filter(Dass21.id == item["id"]).first()
        if exists:
            continue

        record = Dass21(
            id=item["id"],
            statement=item["statement"],
            category=item["category"]
        )
        db.add(record)

    db.commit()
    print(">> Seeding DASS21 selesai!")

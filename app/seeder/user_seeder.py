import csv
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, RoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_user_data(db: Session):
    current_dir = os.path.dirname(__file__)                       # /app/seeder
    csv_path = os.path.join(current_dir, "data", "users.csv")     # /app/seeder/data/users.csv

    print(f"Loading User data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(User).filter(User.id == int(row["id"])).first()
            if exists:
                print(f"Skipping ID {row['id']} - already exists")
                continue

            hashed_pw = pwd_context.hash(row["password"])

            user = User(
                id=int(row["id"]),
                username=row["username"],
                email=row["email"],
                hashed_password=hashed_pw,   # password sudah di-hash
                role=RoleEnum(row["role"])
            )

            db.add(user)

    db.commit()
    print("User seeding completed!")

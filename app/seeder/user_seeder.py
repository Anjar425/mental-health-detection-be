import csv
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, RoleEnum

# MENGGUNAKAN PBKDF2_SHA256: Algoritma hashing yang aman dan tidak bermasalah
# dengan batas 72 byte yang terus muncul.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
def seed_user_data(db: Session):
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "data", "users.csv")

    print(f"Loading User data from: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Menggunakan .strip() untuk memastikan tidak ada spasi ekstra dari CSV
            user_id = int(row["id"].strip()) 
            
            exists = db.query(User).filter(User.id == user_id).first()
            if exists:
                print(f"Skipping ID {user_id} - already exists")
                continue

            raw_password = row["password"]
            
            try:
                # Password di-hash menggunakan PBKDF2_SHA256
                hashed_pw = pwd_context.hash(raw_password)
            except Exception as e:
                # Menangkap error jika masih terjadi
                print(f"FATAL ERROR on user ID {user_id} during hashing: {e}")
                raise e
            
            user = User(
                id=user_id,
                username=row["username"].strip(),
                email=row["email"].strip(),
                hashed_password=hashed_pw,
                role=RoleEnum(row["role"].strip())
            )

            db.add(user)

    db.commit()
    print("User seeding completed!")
import sys
import os

# Trik agar folder 'app' terbaca dari root
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models import User, RoleEnum
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
# Import model lain jika perlu
from sqlalchemy import text

def seed_user_data(db):
    """Seed users into provided DB session. Used by `run_seeders()`."""
    try:
        print("🗑️  Membersihkan data user lama...")
        # Hapus semua data user (Reset ID sequence di SQLite agak tricky, tapi delete all sudah cukup)
        db.execute(text("DELETE FROM users;")) 
        db.commit()

        print("🌱 Memulai Seeding Data Baru (4 Expert + 22 User)...")
        
        users_list = [
            # --- 4 EXPERTS ---
            {"id": 1, "username": "expert1", "email": "expert1@example.com", "password": "sandiAman123", "role": "expert"},
            {"id": 2, "username": "expert2", "email": "expert2@example.com", "password": "sandiAman123", "role": "expert"},
            {"id": 3, "username": "expert3", "email": "expert3@example.com", "password": "sandiAman123", "role": "expert"},
            {"id": 4, "username": "expert4", "email": "expert4@example.com", "password": "sandiAman123", "role": "expert"},
            
            # --- 22 USERS (Mulai ID 5 sampai 26) ---
            {"id": 5, "username": "user1", "email": "user1@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 6, "username": "user2", "email": "user2@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 7, "username": "user3", "email": "user3@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 8, "username": "user4", "email": "user4@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 9, "username": "user5", "email": "user5@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 10, "username": "user6", "email": "user6@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 11, "username": "user7", "email": "user7@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 12, "username": "user8", "email": "user8@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 13, "username": "user9", "email": "user9@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 14, "username": "user10", "email": "user10@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 15, "username": "user11", "email": "user11@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 16, "username": "user12", "email": "user12@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 17, "username": "user13", "email": "user13@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 18, "username": "user14", "email": "user14@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 19, "username": "user15", "email": "user15@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 20, "username": "user16", "email": "user16@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 21, "username": "user17", "email": "user17@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 22, "username": "user18", "email": "user18@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 23, "username": "user19", "email": "user19@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 24, "username": "user20", "email": "user20@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 25, "username": "user21", "email": "user21@example.com", "password": "sandiAman123", "role": "user"},
            {"id": 26, "username": "user22", "email": "user22@example.com", "password": "sandiAman123", "role": "user"},
        ]

        count = 0
        for data in users_list:
            # Kita paksa insert tanpa cek exist karena tabel sudah dikosongkan di atas
            # Hash password and convert role string to RoleEnum
            hashed_pw = pwd_context.hash(data["password"])
            new_user = User(
                id=data["id"],
                username=data["username"],
                email=data["email"],
                hashed_password=hashed_pw,
                role=RoleEnum(data["role"])
            )
            db.add(new_user)
            count += 1

        db.commit()
        print(f"✅ SUKSES! {count} user berhasil dimasukkan.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()


def reset_and_seed():
    print("🔄 Menghubungkan ke database...")
    db = SessionLocal()
    try:
        seed_user_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
import sys
import os

# ==============================================================================
# BAGIAN PENTING: Fix Path (Wajib ada di paling atas)
# Ini memberitahu Python bahwa folder root ada di 2 tingkat di atas folder ini.
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__)) # Lokasi file ini (app/seeder)
root_dir = os.path.abspath(os.path.join(current_dir, "../../")) # Naik 2 level ke root
sys.path.append(root_dir) # Masukkan root ke daftar path python
# ==============================================================================

from app.database import SessionLocal
from app.models import User
# Jika RoleEnum tidak ada di models.py, hapus import RoleEnum di bawah ini
# dan gunakan string "admin" langsung.
try:
    from app.models import RoleEnum
except ImportError:
    RoleEnum = None

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def seed_admin(db=None):
    """Create default admin if missing. Accepts an optional DB session.
    If db is not provided, a new session is created and closed here."""
    created_local_session = False
    if db is None:
        db = SessionLocal()
        created_local_session = True

    try:
        print("🌱 Memeriksa data Admin...")

        admin_email = "admin@example.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()

        if existing_admin:
            print(f"⚠️ Skipped: Admin {admin_email} sudah ada.")
            return

        # Create hashed password and set role properly
        hashed = pwd_context.hash("admin123")

        role_value = RoleEnum.admin if RoleEnum is not None else "admin"

        new_admin = User(
            username="admin",
            email=admin_email,
            hashed_password=hashed,
            role=role_value
        )
        db.add(new_admin)
        db.commit()
        print(f"✅ SUKSES! Admin berhasil dibuat: {admin_email}")

    except Exception as e:
        print(f"❌ Terjadi Error: {e}")
        db.rollback()
        raise
    finally:
        if created_local_session:
            db.close()

if __name__ == "__main__":
    seed_admin()
"""Utility script to create default admin user (safe to run multiple times).

Usage: python scripts/create_admin.py
"""
from app.database import SessionLocal
from app.models import User, RoleEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def create_admin():
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "admin@example.com").first()
    if existing:
        print("Admin already exists")
        return
    hashed_pw = pwd_context.hash("admin123")
    admin = User(username="admin", email="admin@example.com", hashed_password=hashed_pw, role=RoleEnum.admin)
    db.add(admin)
    db.commit()
    print("Admin user created: admin@example.com")

if __name__ == '__main__':
    create_admin()

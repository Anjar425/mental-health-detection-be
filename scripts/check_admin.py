from app.database import SessionLocal
from app.models import User

db = SessionLocal()
admin = db.query(User).filter(User.email=='admin@example.com').first()
if admin:
    print('FOUND_ADMIN', admin.id, admin.email, admin.role)
else:
    print('ADMIN_NOT_FOUND')

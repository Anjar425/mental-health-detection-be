from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
print('Users in database:')
for user in users:
    print(f'  {user.id}: {user.username} ({user.email}) - {user.role}')
db.close()
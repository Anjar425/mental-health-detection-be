from app.database import SessionLocal
from app.models import ExpertGroup

db = SessionLocal()
groups = db.query(ExpertGroup).all()
print('Groups in database:')
for group in groups:
    print(f'  {group.id}: {group.name} - {group.description} - Members: {len(group.experts)}')
db.close()
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('assessment_history')
print('Columns in assessment_history:')
for col in columns:
    print(f'  {col["name"]}: {col["type"]}')
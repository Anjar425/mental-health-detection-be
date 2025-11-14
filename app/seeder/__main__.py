from app.database import SessionLocal
from app.seeder.dass21 import seed_dass21_data
from app.seeder.dass42 import seed_dass42_data


def run_seeders():
    """
    Jalankan semua seeder di folder seeder/
    """
    db = SessionLocal()

    print("=== Running Seeder ===")

    seed_dass21_data(db)
    seed_dass42_data(db)

    print("=== Seeder Completed ===")

if __name__ == "__main__":
    run_seeders()
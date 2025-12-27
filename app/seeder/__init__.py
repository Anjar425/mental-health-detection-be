from app.database import SessionLocal, engine, Base
from app.seeder.dass21 import seed_dass21_data
from app.seeder.dass42 import seed_dass42_data
from .user_seeder import seed_user_data
from .expert_group_seeder import seed_expert_groups
from .preferences_seeder import seed_preference_data
from .expert_profiles_seeder import seed_expert_profile_data
from .expert_weight_seeder import seed_expert_weight_data
from .category_seeder import seed_category_data
from .severity_seeder import seed_severity_data
from .conclusion_seeder import seed_conclusion_data
from .rule_seeder import seed_rule_data
from .premise_seeder import seed_premise_data
from .admin_seeder import seed_admin


def run_seeders():
    """
    Jalankan semua seeder di folder seeder/
    """
    db = SessionLocal()

    print("=== Running Seeder ===")

    # Ensure DB tables exist (useful for initial setup/testing)
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    seed_dass21_data(db)
    seed_dass42_data(db)
    seed_user_data(db)
    seed_expert_groups(db)
    # Seed admin user explicitly (ensures admin even if CSV lacks it)
    seed_admin(db)
    seed_preference_data(db)
    seed_expert_profile_data(db)
    seed_expert_weight_data(db)
    seed_category_data(db)
    seed_severity_data(db)
    seed_conclusion_data(db)
    seed_rule_data(db)
    seed_premise_data(db)

    print("=== Seeder Completed ===")

if __name__ == "__main__":
    run_seeders()
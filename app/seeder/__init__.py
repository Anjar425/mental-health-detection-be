from app.database import SessionLocal
from app.seeder.dass21 import seed_dass21_data
from app.seeder.dass42 import seed_dass42_data
from .user_seeder import seed_user_data
from .preferences_seeder import seed_preference_data
from .expert_profiles_seeder import seed_expert_profile_data
from .expert_weight_seeder import seed_expert_weight_data
from .category_seeder import seed_category_data
from .severity_seeder import seed_severity_data
from .conclusion_seeder import seed_conclusion_data
from .rule_seeder import seed_rule_data
from .premise_seeder import seed_premise_data


def run_seeders():
    """
    Jalankan semua seeder di folder seeder/
    """
    db = SessionLocal()

    print("=== Running Seeder ===")

    seed_dass21_data(db)
    seed_dass42_data(db)
    seed_user_data(db)
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
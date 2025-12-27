import random
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, RoleEnum
from app.models.expert_group import ExpertGroup

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DEFAULT_PASSWORD = "password123"

GROUP_NAMES = [
    "Clinical Psychology",
    "Child Development",
    "Cognitive Therapy",
    "Neuropsychology",
    "Behavioral Science"
]

DUMMY_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Edward",
    "Fiona", "George", "Hannah", "Ian", "Julia",
    "Kevin", "Laura", "Michael", "Nina", "Oscar"
]

def seed_expert_groups(db: Session):
    # 1. Create "Group 1" if not exists
    group1 = db.query(ExpertGroup).filter(ExpertGroup.name == "Group 1").first()
    if not group1:
        group1 = ExpertGroup(name="Group 1", description="Default group for initial experts")
        db.add(group1)
        db.commit()
        db.refresh(group1)

    # Find existing 4 experts (lowest 4 expert IDs)
    experts = db.query(User).filter(User.role == RoleEnum.expert).order_by(User.id.asc()).limit(4).all()
    for expert in experts:
        if expert not in group1.experts:
            group1.experts.append(expert)
    db.commit()

    # 2. Create 5 new groups if not exist
    groups = []
    for name in GROUP_NAMES:
        group = db.query(ExpertGroup).filter(ExpertGroup.name == name).first()
        if not group:
            group = ExpertGroup(name=name, description=f"Group for {name}")
            db.add(group)
            db.commit()
            db.refresh(group)
        groups.append(group)

    # 3. Generate 15 new experts
    new_experts = []
    for idx, name in enumerate(DUMMY_NAMES):
        username = f"dummyexpert{idx+1}"
        email = f"{username}@example.com"
        hashed_pw = pwd_context.hash(DEFAULT_PASSWORD)
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_pw,
                role=RoleEnum.expert
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        new_experts.append(user)

    # 4. Randomly assign new experts to groups (some to multiple groups)
    for expert in new_experts:
        # Each expert gets 1-3 random groups
        n_groups = random.randint(1, 3)
        assigned_groups = random.sample(groups, n_groups)
        for group in assigned_groups:
            if expert not in group.experts:
                group.experts.append(expert)
        db.commit()

    print("Expert group seeding completed.")

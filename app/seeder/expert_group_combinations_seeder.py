from itertools import combinations
from sqlalchemy.orm import Session
from app.models import User, RoleEnum
from app.models.expert_group import ExpertGroup


def seed_expert_group_combinations(db: Session):
    """
    Create all possible expert group combinations (size 2 and 3) from the first four experts.
    Total combinations: C(4,2)=6 and C(4,3)=4 -> 10 groups.
    Group names are unique: "Combo E{id1}-{id2}" and "Combo E{id1}-{id2}-{id3}".
    """
    # Fetch first 4 expert users by lowest IDs
    experts = db.query(User).filter(User.role == RoleEnum.expert).order_by(User.id.asc()).limit(4).all()
    if len(experts) < 2:
        print("Not enough experts to create combinations (need at least 2)")
        return

    expert_ids = [e.id for e in experts]

    created = 0

    # Size 2 combinations
    for combo in combinations(expert_ids, 2):
        name = f"Grub E{combo[0]}-{combo[1]}"
        group = db.query(ExpertGroup).filter(ExpertGroup.name == name).first()
        if not group:
            group = ExpertGroup(name=name, description=f"Group of experts {combo[0]}, {combo[1]}")
            db.add(group)
            db.commit()
            db.refresh(group)
        # attach members
        members = db.query(User).filter(User.id.in_(combo)).all()
        for m in members:
            if m not in group.experts:
                group.experts.append(m)
        db.commit()
        created += 1

    # Size 3 combinations
    if len(expert_ids) >= 3:
        for combo in combinations(expert_ids, 3):
            name = f"Grub E{combo[0]}-{combo[1]}-{combo[2]}"
            group = db.query(ExpertGroup).filter(ExpertGroup.name == name).first()
            if not group:
                group = ExpertGroup(name=name, description=f"Group of experts {combo[0]}, {combo[1]}, {combo[2]}")
                db.add(group)
                db.commit()
                db.refresh(group)
            members = db.query(User).filter(User.id.in_(combo)).all()
            for m in members:
                if m not in group.experts:
                    group.experts.append(m)
            db.commit()
            created += 1

    print(f"Expert group combinations seeding completed. Processed {created} combinations.")

from .base_controller import BaseController
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Rule, Category, Conclusion, Severity, Premise, PrefixEnum, ConjunctionEnum, LevelEnum
from ..schemas import RuleCreateOrUpdate

class RulesetController(BaseController):
    def get_user_rules(self, current_user):
        db: Session = next(self.get_session())

        rules = db.query(Rule).filter(Rule.user_id == current_user.id).all()

        formatted = []

        for rule in rules:

            premises_data = []
            for p in rule.premises:
                premises_data.append({
                    "dass42_id": p.dass42_id,
                    "prefix": p.prefix.value if p.prefix else None,
                    "level": p.level.value if p.level else None,
                    "conjunction": p.conjunction.value if p.conjunction else None
                })

            conclusion = rule.conclusion
            conclusion_data = {
                "category": conclusion.category.name if conclusion.category else None,
                "severity": conclusion.severity_data.name if conclusion.severity_data else None
            }

            formatted.append({
                "rule_id": rule.id,
                "rules": {
                    "premises": premises_data,
                    "conclusion": conclusion_data
                }
            })

        return formatted
    
    def create_and_edit_rule(self, data: RuleCreateOrUpdate, current_user):
        db: Session = next(self.get_session())

        # Cari Category
        category = (
            db.query(Category)
            .filter(Category.name == data.conclusion.category)
            .first()
        )
        severity = (
            db.query(Severity)
            .filter(Severity.name == data.conclusion.severity)
            .first()
        )

        if not category or not severity:
            raise HTTPException(status_code=400, detail="Category or severity not found")

        # 🔥 Cari Conclusion yang sudah ada (TIDAK bikin baru)
        conclusion = (
            db.query(Conclusion)
            .filter(
                Conclusion.category_id == category.id,
                Conclusion.severity_id == severity.id
            )
            .first()
        )

        if not conclusion:
            raise HTTPException(status_code=400, detail="Conclusion not found")

        if data.rule_id:
            rule = (
                db.query(Rule)
                .filter(Rule.id == data.rule_id, Rule.user_id == current_user.id)
                .first()
            )

            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found")

            rule.conclusion_id = conclusion.id

            db.query(Premise).filter(Premise.rule_id == data.rule_id).delete()

            for p in data.premises:
                premise = Premise(
                    rule_id=data.rule_id,
                    dass42_id=p.dass42_id,
                    prefix=PrefixEnum(p.prefix),
                    level=LevelEnum(p.level),
                    conjunction=ConjunctionEnum(p.conjunction),
                )
                db.add(premise)

            db.commit()
            return {"message": "Rule updated successfully", "rule_id": data.rule_id}

        rule = Rule(
            user_id=current_user.id,
            conclusion_id=conclusion.id
        )
        db.add(rule)
        db.flush()

        for p in data.premises:
            premise = Premise(
                rule_id=rule.id,
                dass42_id=p.dass42_id,
                prefix=PrefixEnum(p.prefix),
                level=LevelEnum(p.level),
                conjunction=ConjunctionEnum(p.conjunction),
            )
            db.add(premise)

        db.commit()
        return {"message": "Rule created successfully", "rule_id": rule.id}

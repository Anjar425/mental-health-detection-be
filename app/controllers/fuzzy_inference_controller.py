
from .base_controller import BaseController
from sqlalchemy.orm import Session
from sqlalchemy import func
from skfuzzy import control as ctrl
from ..models import Rule, Premise, Category
from .expert_system.expert_system import (
    compute_fuzzy_inference,
    questionnaire,
    depression,
    anxiety,
    stress,
    x_depression,
    x_anxiety,
    x_stress,
)


class FuzzyInferenceController (BaseController):
    def build_fuzzy_rules(self, category_name: str):
        db: Session = next(self.get_session())

        # Map category names to consequents
        consequent_map = {
            "depression": depression,
            "anxiety": anxiety,
            "stress": stress,
        }

        if category_name.lower() not in consequent_map:
            raise ValueError(
                f"Invalid category: {category_name}. Must be one of: depression, anxiety, stress"
            )

        consequent = consequent_map[category_name.lower()]

        # Fuzzy membership mapping
        fuzzy_level_map = {
            "low": "Rendah",
            "med": "Sedang",
            "high": "Tinggi",
        }

        # Mapping severity output
        fuzzy_output_map = {
            "depression": {
                1: "Normal",
                2: "Mild",
                3: "Moderate",
                4: "Severe",
                5: "Extremely Severe"
            },
            "anxiety": {
                1: "Normal",
                2: "Mild",
                3: "Moderate",
                4: "Severe",
                5: "Extremely Severe"
            },
            "stress": {
                1: "Normal",
                2: "Mild",
                3: "Moderate",
                4: "Severe",
                5: "Extremely Severe"
            }
        }

        # Fetch all rules
        db_rules = db.query(Rule).all()
        fuzzy_rules = []

        category_obj = db.query(Category).filter(func.lower(Category.name) == category_name.lower()).first()

        if not category_obj:
            raise ValueError(f"Category '{category_name}' not found in Category table")

        expected_category_id = category_obj.id

        for db_rule in db_rules:

            if not db_rule.conclusion:
                continue

            if db_rule.conclusion.category_id != expected_category_id:
                continue

            premises = db.query(Premise).filter(Premise.rule_id == db_rule.id).all()

            if not premises:
                continue

            antecedent_expr = None

            for premise in premises:

                q_name = f"Q{premise.dass42_id}"

                if q_name not in questionnaire:
                    continue

                fuzzy_label = fuzzy_level_map.get(premise.level.value, "Rendah")

                if fuzzy_label not in questionnaire[q_name].terms:
                    continue

                term = questionnaire[q_name][fuzzy_label]

                # Combine AND / OR
                if antecedent_expr is None:
                    antecedent_expr = term
                elif premise.conjunction.value == "and":
                    antecedent_expr = antecedent_expr & term
                elif premise.conjunction.value == "or":
                    antecedent_expr = antecedent_expr | term

            if antecedent_expr is None:
                continue

            severity_id = db_rule.conclusion.severity_id

            if severity_id not in fuzzy_output_map[category_name.lower()]:
                continue

            output_label = fuzzy_output_map[category_name.lower()][severity_id]

            if output_label not in consequent.terms:
                continue

            consequent_term = consequent[output_label]

            fuzzy_rules.append(ctrl.Rule(antecedent_expr, consequent_term))

        return fuzzy_rules

    def compute_inference(self, input_values: dict, category_name: str):
        db: Session = next(self.get_session())
        
        if db is None:
            raise ValueError("Database session is required")
        
        # Map category to consequent and domain
        consequent_map = {
            "depression": (depression, x_depression),
            "anxiety": (anxiety, x_anxiety),
            "stress": (stress, x_stress),
        }
        
        if category_name.lower() not in consequent_map:
            raise ValueError(f"Invalid category: {category_name}")
        
        consequent, domain = consequent_map[category_name.lower()]
        
        # Build rules from database
        rules = self.build_fuzzy_rules(category_name=category_name)
        
        if not rules:
            raise ValueError(f"No fuzzy rules found for category: {category_name}")
        
        # Compute fuzzy inference
        score, memdeg = compute_fuzzy_inference(rules, input_values, consequent, domain)
        
        return {
            "category": category_name,
            "score": float(score) if score is not None else None,
            "membership_degrees": memdeg,
        }

    def compute_all_inferences(self, input_values: dict):
        db: Session = next(self.get_session())
        results = {}
        
        for category in ["depression", "anxiety", "stress"]:
            try:
                results[category] = self.compute_inference(
                    input_values=input_values, category_name=category
                )
            except Exception as e:
                results[category] = {"error": str(e)}
        
        return results

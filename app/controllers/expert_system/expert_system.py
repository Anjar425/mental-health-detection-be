import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Make 42 Antecedent 
x_questionnaire   = np.arange(0, 4, 1)
questionnaire     = {}

for i in range(1, 43):
    name = f"Q{i}"
    questionnaire[name]   = ctrl.Antecedent(x_questionnaire, name)  
for ques in questionnaire.values():
    ques["Rendah"]        = fuzz.trimf(x_questionnaire, [0.0, 0.0, 1.5])
    ques["Sedang"]        = fuzz.trimf(x_questionnaire, [0.5, 1.5, 2.5]) 
    ques["Tinggi"]        = fuzz.trimf(x_questionnaire, [1.5, 3.0, 3.0])

# Depression domain 0..42 (user: 0-42)
x_depression                   = np.arange(0, 43, 1)
depression                     = ctrl.Consequent(x_depression, "depression")
depression["Normal"]           = fuzz.trapmf(x_depression, [0, 0, 6, 12])
depression["Mild"]             = fuzz.trimf(x_depression, [8, 12, 16])
depression["Moderate"]         = fuzz.trimf(x_depression, [12, 18, 24])
depression["Severe"]           = fuzz.trimf(x_depression, [20, 26, 32])
depression["Extremely Severe"] = fuzz.trapmf(x_depression, [27, 34, 42, 42])

# Anxiety domain 0..41 (user used np.arange(0,42,1) -> 0..41)
x_anxiety                      = np.arange(0, 42, 1)
anxiety                        = ctrl.Consequent(x_anxiety, "anxiety")
anxiety["Normal"]              = fuzz.trimf(x_anxiety, [0, 0, 7])
anxiety["Mild"]                = fuzz.trimf(x_anxiety, [5, 7, 9])
anxiety["Moderate"]            = fuzz.trimf(x_anxiety, [7, 11, 14])
anxiety["Severe"]              = fuzz.trimf(x_anxiety, [12, 16, 19])
anxiety["Extremely Severe"]    = fuzz.trapmf(x_anxiety, [17, 24, 42, 42])

# Stress domain 0..41
x_stress                       = np.arange(0, 42, 1)
stress                         = ctrl.Consequent(x_stress, "stress")
stress["Normal"]               = fuzz.trapmf(x_stress, [0, 0, 7, 14])
stress["Mild"]                 = fuzz.trimf(x_stress, [11, 14, 18])
stress["Moderate"]             = fuzz.trimf(x_stress, [16, 20, 25])
stress["Severe"]               = fuzz.trimf(x_stress, [23, 28, 33])
stress["Extremely Severe"]     = fuzz.trapmf(x_stress, [31, 36, 42, 42])

print(questionnaire)

def get_rules_from_json(consequent_name: str, questionnaire: dict, consequent):
    """
    Read fuzzy rules from a JSON file and generate a list of skfuzzy `ctrl.Rule` objects
    for a single consequent.

    Parameters
    ----------
    consequent_name : str
        The name of the output (consequent) variable, e.g., "depression", "anxiety", or "stress".
        The function will look for a JSON file with the name format:
        `fis-{consequent_name}-rules.json`.

    questionnaire : dict
        A dictionary containing all antecedent variables (e.g., Q1–Q42),
        where each key corresponds to an instance of `ctrl.Antecedent`.

    consequent : ctrl.Consequent
        The fuzzy output variable associated with the rules.

    Returns
    -------
    list of ctrl.Rule
        A list of fuzzy logic rules (Rule objects) created from the JSON file.
    """
    import json
    from skfuzzy import control as ctrl

    filename = f"fis-{consequent_name}-rules.json"
    with open(filename, "r") as f:
        data = json.load(f)

    # Mapping numeric class values (1–5) to fuzzy labels
    class_map = {
        1: "Normal",
        2: "Mild",
        3: "Moderate",
        4: "Severe",
        5: "Extremely Severe"
    }

    rules = []

    for rule_data in data:
        antecedent_expr = None

        # Gabungkan semua Q* menjadi AND
        for key, value in rule_data.items():
            if key.startswith("Q"):
                if key not in questionnaire:
                    raise ValueError(f"Questionnaire missing key: {key}")
                if value not in questionnaire[key].terms:
                    raise ValueError(f"Invalid fuzzy label '{value}' for {key}")
                
                term = questionnaire[key][value]
                antecedent_expr = term if antecedent_expr is None else antecedent_expr & term

        # Ambil class/output
        class_value = rule_data.get("Class")
        class_label = class_map.get(class_value, class_value)

        if class_label not in consequent.terms:
            raise ValueError(f"Invalid class label: {class_label}")

        consequent_term = consequent[class_label]

        # Buat rule dan append
        rule = ctrl.Rule(antecedent_expr, consequent_term)
        rules.append(rule)

    return rules

def get_used_input_variables(rules):
    """
    Extract Antecedent variable labels (Q*) from skfuzzy rules
    supporting nested TermAggregate.term1/term2 structure.
    """
    visited = set()
    found   = set()

    def walk(node):
        if node is None:
            return
        if id(node) in visited:
            return
        visited.add(id(node))

        # Case: Term → parent = Antecedent
        if hasattr(node, "parent"):
            parent = node.parent
            if isinstance(parent, ctrl.Antecedent):
                found.add(parent.label)

        # Case: nested term
        if hasattr(node, "term"):
            walk(node.term)

        # TermAggregate structure
        if hasattr(node, "term1"):
            walk(node.term1)

        if hasattr(node, "term2"):
            walk(node.term2)

        # children (if exist)
        if hasattr(node, "children"):
            for c in node.children:
                walk(c)

    for r in rules:
        walk(r.antecedent)

    return sorted(v for v in found if v.startswith("Q"))

def compute_fuzzy_inference(rules, input_values, consequent, domain):
    """
    Perform fuzzy inference for a single consequent using given rules and specified output variable.

    Parameters
    ----------
    rules : list of ctrl.Rule
        Fuzzy rules for a single consequent (e.g., depression_rules, anxiety_rules, or stress_rules).

    input_values : dict
        Dictionary containing values for all antecedents (Q1..Q42).
        Example: {"Q1": 2, "Q2": 1, "Q3": 3, ..., "Q42": 0}

    consequent : ctrl.Consequent
        The fuzzy output variable (e.g., depression, anxiety, or stress) associated with the rules.

    Returns
    -------
    float
        The defuzzified output value for the specified consequent.
        Returns None if simulation fails.
    """
    # Build fuzzy control system and simulation
    fuzz_ctrl = ctrl.ControlSystem(rules)
    fuzz_sim = ctrl.ControlSystemSimulation(fuzz_ctrl)

    used_inputs = get_used_input_variables(rules)

    # Assign input values yang digunakan di rules
    for key in used_inputs:
        if key in input_values:
            fuzz_sim.input[key] = input_values[key]
        else:
            # Jika input tidak ada di input_values, lempar error atau skip (pilih sesuai kebutuhan)
            pass

    # Compute fuzzy inference with error handling
    try:
        fuzz_sim.compute()
        # Get defuzzified output for the specified consequent
        result = fuzz_sim.output[consequent.label]

        memdeg = {}
        for label in consequent.terms:
            mf = consequent[label].mf
            memdeg[label] = float(fuzz.interp_membership(domain, mf, result))

    except Exception as e:
        print(f"[ERROR] Fuzzy simulation failed for {consequent.label}: {e}")
        result = None

    return result, memdeg
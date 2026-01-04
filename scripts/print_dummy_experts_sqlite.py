import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT, "test.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

usernames = [f"dummyexpert{i}" for i in range(4,9)]

for uname in usernames:
    cur.execute("SELECT id, username, email FROM users WHERE username = ?", (uname,))
    row = cur.fetchone()
    if not row:
        print(f"User {uname} not found")
        continue
    uid, username, email = row
    print("===", username, f"(id={uid})", "===")
    print("email:", email)
    # Profile
    cur.execute("SELECT education_level, publication_count, patient_count, flight_hours FROM expert_profiles WHERE user_id = ?", (uid,))
    p = cur.fetchone()
    print("Profile:")
    if p:
        print("  education_level:", p[0])
        print("  publication_count:", p[1])
        print("  patient_count:", p[2])
        print("  flight_hours:", p[3])
    else:
        print("  No profile")
    # Weights
    cur.execute("SELECT education_weight, patient_weight, publication_weight, flight_hours_weight FROM expert_weights WHERE user_id = ?", (uid,))
    w = cur.fetchone()
    print("Weights (percentages):")
    if w:
        print("  education_weight:", w[0])
        print("  patient_weight:", w[1])
        print("  publication_weight:", w[2])
        print("  flight_hours_weight:", w[3])
    else:
        print("  No weights")
    # Preferences
    cur.execute("SELECT dass21_id, percent_depression, percent_anxiety, percent_stress FROM preferences WHERE user_id = ? ORDER BY dass21_id", (uid,))
    prefs = cur.fetchall()
    print("Preferences (dass21_id -> dep/anx/stress):")
    if prefs:
        for p in prefs:
            print(f"  {p[0]}: dep={p[1]}, anx={p[2]}, stress={p[3]}")
    else:
        print("  No preferences")
    print()

conn.close()

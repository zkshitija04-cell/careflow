import random
from datetime import datetime, timedelta
import pandas as pd

# Makes the random numbers repeat the same way every run
random.seed(42)

# ----- Settings you can change later -----
NUM_PATIENTS = 500
LOOP_BACK_RATE = 0.40      # 40% go back to Triage after the X-Ray
SKIP_TRIAGE_RATE = 0.03    # 3% skip Triage (rule-breakers)

# Average waiting time (in minutes) before each step
AVG_WAIT = {
    "Registration": 0,
    "Triage": 10,
    "X-Ray": 20,
    "Doctor Consultation": 30,
    "Discharge": 15,
}

# Which staff member handles each step
STAFF = {
    "Registration": ["Front Desk A", "Front Desk B"],
    "Triage": ["Nurse Asha", "Nurse Ravi", "Nurse Meera"],
    "X-Ray": ["Tech Imran", "Tech Priya"],
    "Doctor Consultation": ["Dr. Rao", "Dr. Iyer", "Dr. Khan"],
    "Discharge": ["Front Desk A", "Front Desk B"],
}

rows = []
first_day = datetime(2026, 1, 1, 8, 0, 0)

for n in range(1, NUM_PATIENTS + 1):
    case_id = f"P{n:04d}"   # P0001, P0002, ...

    # Each patient arrives at a random time during January
    current_time = first_day + timedelta(
        days=random.randint(0, 29),
        minutes=random.randint(0, 600),
    )

    # Decide which path this patient takes
    dice = random.random()
    if dice < LOOP_BACK_RATE:
        path = ["Registration", "Triage", "X-Ray", "Triage",
                "Doctor Consultation", "Discharge"]
    elif dice < LOOP_BACK_RATE + SKIP_TRIAGE_RATE:
        path = ["Registration", "X-Ray", "Doctor Consultation", "Discharge"]
    else:
        path = ["Registration", "Triage", "X-Ray",
                "Doctor Consultation", "Discharge"]

    # Walk through each step, adding a random wait before it
    for activity in path:
        avg = AVG_WAIT[activity]
        if avg > 0:
            wait = random.randint(max(1, avg // 2), avg * 2)
            current_time += timedelta(minutes=wait)

        rows.append({
            "case_id": case_id,
            "activity": activity,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "resource": random.choice(STAFF[activity]),
        })

# Turn the list into a table and save it as a CSV file
df = pd.DataFrame(rows)
df.to_csv("ehr_events.csv", index=False)

# Quick summary so you can check the result
triage_counts = df[df["activity"] == "Triage"].groupby("case_id").size()
loop_backs = (triage_counts > 1).sum()
print("Patients:", df["case_id"].nunique())
print("Total events:", len(df))
print("Patients sent back to Triage:", loop_backs)
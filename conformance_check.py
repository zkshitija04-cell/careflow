import pandas as pd
import pm4py

# The correct path the hospital wants everyone to follow
IDEAL = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

# 1. Read the data and put each patient's steps in time order
df = pd.read_csv("ehr_events.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["case_id", "timestamp"])

# 2. Build each patient's journey as a list of steps
paths = df.groupby("case_id")["activity"].apply(list)

# 3. Compare one journey with the correct path
def check(path):
    if path == IDEAL:
        return "Compliant", ""
    reasons = []
    for step in IDEAL:
        if step not in path:
            reasons.append("Skipped " + step)
    for step in sorted(set(path)):
        if path.count(step) > 1:
            reasons.append("Repeated " + step)
    if not reasons:
        reasons.append("Steps out of order")
    return "Non-compliant", "; ".join(reasons)

# 4. Check every patient
rows = []
for case_id, path in paths.items():
    status, reason = check(path)
    rows.append({
        "case_id": case_id,
        "status": status,
        "reason": reason,
        "path": " -> ".join(path),
    })

results = pd.DataFrame(rows)
results.to_csv("conformance_results.csv", index=False)
results[results["status"] == "Non-compliant"].to_csv("non_compliant_cases.csv", index=False)

# 5. Print the summary
total = len(results)
bad = (results["status"] == "Non-compliant").sum()
print("Patients checked:", total)
print("Compliant:", total - bad)
print("Non-compliant:", bad, f"({bad / total * 100:.1f}%)")
print()
print("Reasons:")
print(results[results["status"] == "Non-compliant"]["reason"].value_counts().to_string())

# 6. Same check done the PM4Py way (token replay on a model of the correct path)
ideal_df = pd.DataFrame({
    "case:concept:name": ["ideal"] * len(IDEAL),
    "concept:name": IDEAL,
    "time:timestamp": pd.date_range("2026-01-01 08:00", periods=len(IDEAL), freq="15min"),
})
net, im, fm = pm4py.discover_petri_net_inductive(ideal_df)
pm4py.save_vis_petri_net(net, im, fm, "ideal_process.png")

actual = df.rename(columns={
    "case_id": "case:concept:name",
    "activity": "concept:name",
    "timestamp": "time:timestamp",
})
fitness = pm4py.fitness_token_based_replay(actual, net, im, fm)
print()
print("PM4Py fitness result (1.0 = perfect match):")
print(fitness)
import pandas as pd

# 1. Read the data and put each patient's steps in time order
df = pd.read_csv("ehr_events.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["case_id", "timestamp"])

# 2. On each row, look at the NEXT row of the same patient
df["next_activity"] = df.groupby("case_id")["activity"].shift(-1)
df["next_time"] = df.groupby("case_id")["timestamp"].shift(-1)

# 3. Minutes between this step and the next one
df["wait_minutes"] = (df["next_time"] - df["timestamp"]).dt.total_seconds() / 60

# 4. Drop each patient's last step (nothing comes after Discharge)
steps = df.dropna(subset=["next_activity"])

# 5. Average the waiting time for each pair of steps
table = (
    steps.groupby(["activity", "next_activity"])["wait_minutes"]
    .agg(patients="count", avg_wait="mean", longest="max")
    .round(1)
    .reset_index()
    .sort_values("avg_wait", ascending=False)
)
table.to_csv("transition_times.csv", index=False)

print("WAITING TIME BETWEEN STEPS (slowest first)")
print(table.to_string(index=False))

# 6. Total time each patient spent in the hospital
stay = df.groupby("case_id")["timestamp"].agg(["min", "max"])
stay["total_minutes"] = (stay["max"] - stay["min"]).dt.total_seconds() / 60

# 7. Was this patient sent back to Triage?
triage_visits = df[df["activity"] == "Triage"].groupby("case_id").size()
stay["triage_visits"] = triage_visits
stay["looped_back"] = stay["triage_visits"].fillna(0) > 1
stay.to_csv("case_summary.csv")

print()
print("AVERAGE TOTAL TIME IN HOSPITAL (minutes)")
print("Sent back to Triage:  ", round(stay[stay["looped_back"]]["total_minutes"].mean(), 1))
print("Not sent back:        ", round(stay[~stay["looped_back"]]["total_minutes"].mean(), 1))
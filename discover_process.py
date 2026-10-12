import pandas as pd
import pm4py

# 1. Read the CSV file we created earlier
df = pd.read_csv("ehr_events.csv")

# 2. Rename the columns to the names PM4Py expects
df = df.rename(columns={
    "case_id": "case:concept:name",   # which patient
    "activity": "concept:name",       # which step
    "timestamp": "time:timestamp",    # when it happened
})

# 3. Turn the timestamp text into real dates, and sort the rows
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
df = df.sort_values(["case:concept:name", "time:timestamp"])

# 4. Count how many patients took each path
variants = pm4py.get_variants(df)
print("Different paths found:", len(variants))
print()
for path, count in sorted(variants.items(), key=lambda x: x[1], reverse=True):
    print(count, "patients:", " -> ".join(path))

# 5. Draw map 1: how MANY patients move between each pair of steps
dfg, start_acts, end_acts = pm4py.discover_dfg(df)
pm4py.save_vis_dfg(dfg, start_acts, end_acts, file_path="map_frequency.png")

# 6. Draw map 2: how LONG patients wait between each pair of steps
perf_dfg, perf_start, perf_end = pm4py.discover_performance_dfg(df)
pm4py.save_vis_performance_dfg(perf_dfg, perf_start, perf_end, file_path="map_waiting_time.png")

print()
print("Done. Two pictures saved: map_frequency.png and map_waiting_time.png")
import pandas as pd

# File 1: one row per patient, with total time in the hospital
summary = pd.read_csv("case_summary.csv")
print("Average total minutes in hospital:")
print("(False = not sent back, True = sent back to Triage)")
print(summary.groupby("looped_back")["total_minutes"].mean().round(1))

# File 2: one row per patient, with compliant or non-compliant
results = pd.read_csv("conformance_results.csv")
print()
print("Patients who followed the correct path:")
print(results["status"].value_counts())
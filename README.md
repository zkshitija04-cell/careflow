# CareFlow: Clinical Pathway Process Mining

Hospital dashboards show the average ER wait time, but not the real sequence of steps each patient goes through. CareFlow reads timestamped event logs, discovers the actual patient path with process mining, and finds where the process breaks down.

## The problem found

- Patients sent back to Triage stayed **107.4 minutes** on average, versus **93.5 minutes** for patients who were not, about **13.9 minutes (15%) longer**.
- Conformance check: **303 of 500 patients (60.6%)** followed the correct path. **197 (39.4%)** did not: 177 repeated Triage and 20 skipped it.
- Business action this points to: fix the cause of the X-Ray-to-Triage rework (for example, a missing intake form) to reduce stay time for about 1 in 3 patients.

## Architecture

```
generate_logs.py  ->  ehr_events.csv  ->  BigQuery (raw_ehr_events)
                                              |
                                          dbt models
                                              |
                              stg_ehr_events -> event_log (Case_ID, Activity_Name, Timestamp)

PM4Py: process maps, wait times, conformance check
Power BI dashboard: planned
```

## Tools

| Tool | Used for |
|---|---|
| Python 3.12, pandas | Data generation and analysis |
| PM4Py + Graphviz | Process discovery and process maps |
| Google BigQuery (sandbox) | Data warehouse |
| dbt (dbt-bigquery) | Cleaning and standardizing the event log |
| Git / GitHub | Version control |

## What is in this repository

| File or folder | What it does |
|---|---|
| `generate_logs.py` | Creates 500 simulated patients and 2,657 events, with a deliberate 40% target loop-back and a few skipped steps |
| `discover_process.py` | Finds the distinct patient paths and draws two process maps (frequency and waiting time) |
| `bottleneck_analysis.py` | Calculates the average wait between every pair of steps and the total hospital time |
| `conformance_check.py` | Compares each patient with the ideal path and flags non-compliant cases with a reason |
| `db/careflow_dbt/` | dbt project: staging view, `event_log` table, and 7 data quality tests |
| `db/sql/` and `db/BIGQUERY_SETUP.md` | BigQuery setup notes and verification checks |

## Data quality checks

- BigQuery row count (2,657) matches the Python output
- Patients sent back to Triage: 177, identical in Python and in SQL
- dbt tests: 7 of 7 passing (no empty values; activity names limited to the five known steps)

## How to run

1. Install the tools: `pip install pandas numpy faker pm4py dbt-bigquery`, and install Graphviz
2. `python generate_logs.py` creates `ehr_events.csv`
3. Load the CSV into BigQuery as `raw_ehr_events`
4. From `db/careflow_dbt`: `dbt run`, then `dbt test`
5. `python discover_process.py`, `python bottleneck_analysis.py`, `python conformance_check.py`

## Note on the data

Real patient data is private, so all records are simulated. The patient paths, waiting times, and the loop-back rate are set in `generate_logs.py`.

## Status and next steps

- [x] Event log generation
- [x] BigQuery warehouse
- [x] dbt cleaning models and tests
- [x] Process discovery with PM4Py
- [x] Bottleneck analysis
- [x] Conformance checking
- [ ] Wait-time model in dbt (SQL)
- [ ] Power BI dashboard
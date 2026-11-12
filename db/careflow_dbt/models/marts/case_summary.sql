{{ config(materialized='table') }}

select
    Case_ID,
    min(`Timestamp`) as start_time,
    max(`Timestamp`) as end_time,
    timestamp_diff(max(`Timestamp`), min(`Timestamp`), minute) as total_minutes,
    countif(Activity_Name = 'Triage') as triage_visits,
    countif(Activity_Name = 'Triage') > 1 as looped_back,
    countif(Activity_Name = 'Triage') = 0 as skipped_triage
from {{ ref('event_log') }}
group by Case_ID
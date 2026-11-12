{{ config(materialized='table') }}

with steps as (
    select
        Case_ID,
        Activity_Name,
        `Timestamp` as event_time,
        lead(Activity_Name) over (partition by Case_ID order by `Timestamp`) as next_activity,
        lead(`Timestamp`) over (partition by Case_ID order by `Timestamp`) as next_time
    from {{ ref('event_log') }}
)

select
    Activity_Name as from_activity,
    next_activity as to_activity,
    count(*) as patients,
    round(avg(timestamp_diff(next_time, event_time, minute)), 1) as avg_wait_minutes,
    max(timestamp_diff(next_time, event_time, minute)) as longest_wait_minutes
from steps
where next_activity is not null
group by from_activity, to_activity
order by avg_wait_minutes desc
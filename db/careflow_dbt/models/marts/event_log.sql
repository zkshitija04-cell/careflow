{{ config(materialized='table') }}

select
    case_id as Case_ID,
    activity_name as Activity_Name,
    event_timestamp as `Timestamp`
from {{ ref('stg_ehr_events') }}
order by case_id, event_timestamp
with source as (
    select * from {{ source('careflow', 'raw_ehr_events') }}
)

select distinct
    cast(case_id as string) as case_id,
    trim(activity) as activity_name,
    cast(`timestamp` as timestamp) as event_timestamp,
    resource
from source
where case_id is not null
  and activity is not null
  and `timestamp` is not null
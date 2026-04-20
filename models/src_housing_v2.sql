{{
    config(
        materialized='table',
        tags=['every_30min'],
        transient=false
    )
}}

SELECT *
FROM {{ ref('src_housing') }}
where c10='maille'

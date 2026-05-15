{{
    config(
        materialized='table',
        tags=['every_30min']
       
    )
}}

SELECT *
FROM {{ ref('src_housing') }}
where c10='maille'

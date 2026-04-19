{{
    config(
        materialized='table'
    )
}}

SELECT *
FROM {{ ref('src_housing') }}
where c10='maille'
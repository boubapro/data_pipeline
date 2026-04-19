{{
    config(
        materialized='table',
        tags=['daily_14h10']
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

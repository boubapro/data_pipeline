{{
    config(
        materialized='table',
        tags=['daily_14h50']
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

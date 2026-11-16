{{
    config(
        materialized='table',
        tags=['every_monday_19h']
    )
}}
SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

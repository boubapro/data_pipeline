{{
    config(
        materialized='table',
        tags=['every_30min']
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

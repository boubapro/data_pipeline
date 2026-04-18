{{
    config(
        materialized='table',
        tags=['daily']
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}
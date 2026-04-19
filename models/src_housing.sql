{{
    config(
        materialized='table',
        tags=['sunday_14h']
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

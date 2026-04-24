{{
    config(
        materialized='table' 
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

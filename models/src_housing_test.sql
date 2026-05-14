{{
    config(
        materialized='table',
        transient=false
    )
}}

SELECT *
FROM {{ source('src_housing_ext', 'loyer') }}

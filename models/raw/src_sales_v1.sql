{{ config(materialized='table', tags=['sources', 'every_monday_19h']) }}
SELECT *
FROM {{ source('src_sales', 'src_sales') }}

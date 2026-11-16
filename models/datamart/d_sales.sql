{{ config(materialized='table', tags=['datamart']) }}

SELECT *
FROM {{ ref('src_sales_v1') }}

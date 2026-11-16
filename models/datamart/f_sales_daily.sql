{{
  config(
    materialized='incremental',
    unique_key='SALE_DATE',
    tags=['datamart']
  )
}}

SELECT
    DATE_TRUNC('DAY', CREATED_AT) AS SALE_DATE,
    COUNT(*) AS NB_TRANSACTIONS,
    SUM(QUANTITY) AS TOTAL_QUANTITY,
    SUM(AMOUNT) AS TOTAL_AMOUNT,
    SUM(PRICE * QUANTITY) AS GROSS_REVENUE
FROM {{ ref('src_sales_v1') }}

{% if is_incremental() %}
WHERE NOT EXISTS (SELECT 1 FROM {{ this }})
   OR CREATED_AT >= (SELECT MAX(SALE_DATE) FROM {{ this }})
{% endif %}

GROUP BY 1

{{
  config(
    materialized='incremental',
    unique_key='SALE_DATE',
    on_schema_change='append_new_columns',
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
   -- fenêtre de recul (jours) pour absorber les données tardives
   OR CREATED_AT >= DATEADD(
       'day',
       -{{ var('incremental_lookback_days', 1) }},
       (SELECT MAX(SALE_DATE) FROM {{ this }})
   )
{% endif %}

GROUP BY 1

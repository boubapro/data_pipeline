{{
  config(
    materialized='incremental',
    unique_key=['YEAR', 'MONTH', 'PRODUCT_ID', 'PRODUCT', 'CATEGORY'],
    on_schema_change='append_new_columns',
    tags=['datamart']
  )
}}
{% if is_incremental() %}
WITH _wm AS (
    SELECT MAX(YEAR::NUMBER * 12 + MONTH::NUMBER) AS max_ym
    FROM {{ this }}
)
SELECT
    s.YEAR,
    s.MONTH,
    s.PRODUCT_ID,
    s.PRODUCT,
    s.CATEGORY,
    COUNT(*)            AS NB_TRANSACTIONS,
    SUM(s.QUANTITY)     AS TOTAL_QUANTITY,
    SUM(s.AMOUNT)       AS TOTAL_AMOUNT,
    AVG(s.PRICE)        AS AVG_PRICE
FROM {{ ref('src_sales_v1') }} s
-- Fenêtre de recul : les mois récents sont recalculés pour absorber
-- les données tardives (variable incremental_lookback_months, défaut 1).
WHERE (SELECT max_ym FROM _wm) IS NULL
   OR (s.YEAR::NUMBER * 12 + s.MONTH::NUMBER)
      >= (SELECT max_ym FROM _wm) - {{ var('incremental_lookback_months', 1) }}
GROUP BY 1, 2, 3, 4, 5

{% else %}

    SELECT
        YEAR,
        MONTH,
        PRODUCT_ID,
        PRODUCT,
        CATEGORY,
        COUNT(*) AS NB_TRANSACTIONS,
        SUM(QUANTITY) AS TOTAL_QUANTITY,
        SUM(AMOUNT) AS TOTAL_AMOUNT,
        AVG(PRICE) AS AVG_PRICE
    FROM {{ ref('src_sales_v1') }}
    GROUP BY 1, 2, 3, 4, 5

{% endif %}

{{
  config(
    materialized='incremental',
    unique_key=['YEAR', 'MONTH', 'PRODUCT_ID', 'PRODUCT', 'CATEGORY'],
    tags=['datamart']
  )
}}
{% if is_incremental() %}
WITH _wm AS (
    SELECT YEAR AS max_year, MONTH AS max_month
    FROM {{ this }}
    ORDER BY YEAR DESC, MONTH DESC
    LIMIT 1
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
WHERE NOT EXISTS (SELECT 1 FROM _wm)
   OR s.YEAR > (SELECT max_year FROM _wm)
   OR (
       s.YEAR = (SELECT max_year FROM _wm)
       AND s.MONTH >= (SELECT max_month FROM _wm)
   )
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

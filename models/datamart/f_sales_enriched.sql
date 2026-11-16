{{
  config(
    materialized='table',
    tags=['datamart', 'performance']
  )
}}

SELECT
    s.created_at AS sale_timestamp,
    s.year,
    s.month,
    s.distributor,
    s.product_id,
    s.product,
    s.category,
    s.quantity,
    s.price,
    s.amount,
    p.current_price,
    daily.nb_transactions AS daily_transactions,
    daily.total_amount AS daily_total_amount,
    product_month.total_quantity AS monthly_product_quantity,
    product_month.total_amount AS monthly_product_amount,
    distributor_month.total_quantity AS monthly_distributor_quantity,
    distributor_month.total_amount AS monthly_distributor_amount
FROM {{ ref('f_sales') }} AS s
LEFT JOIN {{ ref('d_product') }} AS p
    ON s.product_id = p.product_id
LEFT JOIN {{ ref('f_sales_daily') }} AS daily
    ON CAST(s.created_at AS DATE) = CAST(daily.sale_date AS DATE)
LEFT JOIN {{ ref('f_sales_by_product') }} AS product_month
    ON
        s.year = product_month.year
        AND s.month = product_month.month
        AND s.product_id = product_month.product_id
        AND s.product = product_month.product
        AND s.category = product_month.category
LEFT JOIN {{ ref('f_sales_by_distributor') }} AS distributor_month
    ON
        s.year = distributor_month.year
        AND s.month = distributor_month.month
        AND s.distributor = distributor_month.distributor

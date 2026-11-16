{{ config(materialized='table', tags=['datamart']) }}

SELECT
    PRODUCT_ID,
    PRODUCT,
    CATEGORY,
    PRICE AS CURRENT_PRICE
FROM {{ ref('src_sales_v1') }}
QUALIFY ROW_NUMBER() OVER (
        PARTITION BY PRODUCT_ID
        ORDER BY CREATED_AT DESC, PRICE DESC, PRODUCT DESC, CATEGORY DESC
    ) = 1

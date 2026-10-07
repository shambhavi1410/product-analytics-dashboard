-- Order-fulfilment funnel. Olist has no click-stream, so the funnel follows the order lifecycle:
-- Purchased -> Approved -> Shipped -> Delivered -> Reviewed.
-- A stage is "reached" when its timestamp is not NULL.
WITH base AS (
    SELECT o.*
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE 1 = 1
    /*FILTERS*/
),
stages AS (
    SELECT 1 AS step, 'Purchased' AS stage, COUNT(*) AS orders FROM base
    UNION ALL SELECT 2, 'Approved',  COUNT(*) FROM base WHERE order_approved_at IS NOT NULL
    UNION ALL SELECT 3, 'Shipped',   COUNT(*) FROM base WHERE order_delivered_carrier_date IS NOT NULL
    UNION ALL SELECT 4, 'Delivered', COUNT(*) FROM base WHERE order_delivered_customer_date IS NOT NULL
    UNION ALL SELECT 5, 'Reviewed',  COUNT(*) FROM base b
              WHERE b.order_delivered_customer_date IS NOT NULL
                AND EXISTS (SELECT 1 FROM order_reviews r WHERE r.order_id = b.order_id)
)
SELECT
    step, stage, orders,
    ROUND(100.0 * orders / FIRST_VALUE(orders) OVER (ORDER BY step), 1) AS pct_of_start,
    ROUND(100.0 * orders / LAG(orders) OVER (ORDER BY step), 1)         AS pct_of_previous
FROM stages
ORDER BY step;

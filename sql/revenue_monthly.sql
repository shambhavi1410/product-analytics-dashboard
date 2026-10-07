-- Monthly revenue, orders, customers, AOV and month-over-month growth.
-- LAG() is a window function: it looks at the previous row (previous month) without a self-join.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp)                       AS month,
        COUNT(DISTINCT o.order_id)                                          AS orders,
        COUNT(DISTINCT c.customer_unique_id)                                AS customers,
        ROUND(SUM(oi.price), 2)                                             AS revenue,
        ROUND(SUM(oi.price) * 1.0 / COUNT(DISTINCT o.order_id), 2)          AS aov
    FROM orders o
    JOIN customers   c  ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id   = o.order_id
    WHERE o.order_status = 'delivered'
    /*FILTERS*/
    GROUP BY month
)
SELECT
    month, orders, customers, revenue, aov,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
          / LAG(revenue) OVER (ORDER BY month), 1)                          AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Sales by customer state.
SELECT
    c.customer_state                                                       AS state,
    COUNT(DISTINCT o.order_id)                                             AS orders,
    COUNT(DISTINCT c.customer_unique_id)                                   AS customers,
    ROUND(SUM(oi.price), 2)                                                AS revenue,
    ROUND(SUM(oi.price) * 1.0 / COUNT(DISTINCT o.order_id), 2)             AS aov,
    ROUND(100.0 * SUM(oi.price) / SUM(SUM(oi.price)) OVER (), 2)           AS revenue_share_pct
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.order_status = 'delivered'
/*FILTERS*/
GROUP BY c.customer_state
ORDER BY revenue DESC;

-- KPIs: headline numbers for the dashboard cards.
-- Only DELIVERED orders count as revenue (cancelled/unavailable orders never earned money).
-- COUNT(DISTINCT order_id) because joining order_items multiplies rows (1 order -> N items).
SELECT
    ROUND(COALESCE(SUM(oi.price), 0), 2)                                              AS revenue,
    COUNT(DISTINCT o.order_id)                                                        AS orders,
    COUNT(DISTINCT c.customer_unique_id)                                              AS customers,
    ROUND(COALESCE(SUM(oi.price), 0) * 1.0 / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS aov,
    ROUND(COALESCE(SUM(oi.freight_value), 0), 2)                                      AS freight
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.order_status = 'delivered'
/*FILTERS*/;

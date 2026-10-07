-- Repeat-purchase summary: what share of customers ordered more than once?
WITH per_customer AS (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    /*FILTERS*/
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*)                                                         AS customers,
    SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END)                    AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_rate_pct,
    ROUND(AVG(n_orders), 3)                                          AS avg_orders_per_customer
FROM per_customer;

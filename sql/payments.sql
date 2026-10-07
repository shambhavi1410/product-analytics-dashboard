-- Payment method mix.
SELECT
    p.payment_type,
    COUNT(DISTINCT o.order_id)             AS orders,
    ROUND(SUM(p.payment_value), 2)         AS payment_value,
    ROUND(AVG(p.payment_installments), 2)  AS avg_installments
FROM orders o
JOIN customers      c ON c.customer_id = o.customer_id
JOIN order_payments p ON p.order_id    = o.order_id
WHERE o.order_status = 'delivered'
/*FILTERS*/
GROUP BY p.payment_type
ORDER BY payment_value DESC;

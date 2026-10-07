-- Delivery performance and customer satisfaction by month.
-- julianday() converts a date to a number of days, so subtracting two gives a duration.
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp)                                        AS month,
    ROUND(AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)), 1) AS avg_delivery_days,
    ROUND(100.0 * AVG(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                           THEN 1 ELSE 0 END), 1)                                        AS late_pct,
    ROUND(AVG(r.review_score), 2)                                                        AS avg_review_score
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN order_reviews r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
/*FILTERS*/
GROUP BY month
ORDER BY month;

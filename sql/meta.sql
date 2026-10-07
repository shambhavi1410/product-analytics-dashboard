-- Values that populate the dashboard's filter widgets.
SELECT 'state' AS kind, customer_state AS value FROM customers GROUP BY customer_state
UNION ALL
SELECT 'month', strftime('%Y-%m', order_purchase_timestamp) FROM orders GROUP BY 2
ORDER BY kind, value;

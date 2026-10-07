-- Cohort retention. Cohort = month of a customer's FIRST delivered order.
-- months_since = how many months after that first order the customer bought again (0 = first month).
-- We use customer_unique_id (a real person); customer_id changes on every order.
WITH orders_c AS (
    SELECT c.customer_unique_id,
           strftime('%Y-%m', o.order_purchase_timestamp) AS order_month
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),
first_order AS (
    SELECT customer_unique_id, MIN(order_month) AS cohort_month
    FROM orders_c
    GROUP BY customer_unique_id
),
activity AS (
    SELECT DISTINCT customer_unique_id, order_month FROM orders_c
),
cohort_counts AS (
    SELECT
        f.cohort_month,
        (CAST(substr(a.order_month, 1, 4) AS INTEGER) - CAST(substr(f.cohort_month, 1, 4) AS INTEGER)) * 12
      + (CAST(substr(a.order_month, 6, 2) AS INTEGER) - CAST(substr(f.cohort_month, 6, 2) AS INTEGER)) AS months_since,
        COUNT(DISTINCT a.customer_unique_id) AS customers
    FROM first_order f
    JOIN activity a ON a.customer_unique_id = f.customer_unique_id
    GROUP BY f.cohort_month, months_since
)
SELECT
    cohort_month, months_since, customers,
    FIRST_VALUE(customers) OVER (PARTITION BY cohort_month ORDER BY months_since) AS cohort_size,
    ROUND(100.0 * customers /
          FIRST_VALUE(customers) OVER (PARTITION BY cohort_month ORDER BY months_since), 2) AS retention_pct
FROM cohort_counts
ORDER BY cohort_month, months_since;

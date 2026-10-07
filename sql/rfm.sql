-- RFM segmentation over each customer's full history (delivered orders).
--   Recency   = days since last order (reference date = newest order in the data)
--   Frequency = number of orders
--   Monetary  = total spend
-- NTILE(5) cuts customers into 5 equal-sized buckets (5 = best).
-- Frequency uses fixed rules because ~97% of customers have exactly ONE order, so quintiles are meaningless.
WITH ref AS (
    SELECT MAX(date(order_purchase_timestamp)) AS ref_date FROM orders
),
customer_metrics AS (
    SELECT
        c.customer_unique_id,
        CAST(julianday((SELECT ref_date FROM ref)) - julianday(MAX(date(o.order_purchase_timestamp))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.price), 2)    AS monetary
    FROM orders o
    JOIN customers   c  ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id   = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 3 ELSE 5 END AS f_score,
        NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM customer_metrics
),
segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 3 THEN 'Champions'
            WHEN f_score >= 3                  THEN 'Loyal Customers'
            WHEN r_score >= 4 AND m_score >= 4 THEN 'New High-Value'
            WHEN r_score >= 4                  THEN 'Recent Buyers'
            WHEN r_score <= 2 AND m_score >= 4 THEN 'At Risk (High-Value)'
            WHEN r_score <= 2                  THEN 'Hibernating'
            ELSE 'Needs Attention'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                                          AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_customers,
    ROUND(AVG(recency_days), 1)                       AS avg_recency_days,
    ROUND(AVG(frequency), 2)                          AS avg_frequency,
    ROUND(AVG(monetary), 2)                           AS avg_monetary,
    ROUND(SUM(monetary), 2)                           AS total_revenue
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;

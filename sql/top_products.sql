-- Product performance by category: revenue, units, share of total and cumulative share (Pareto).
-- English names come from category_translation (LEFT JOIN so untranslated categories survive).
WITH cat AS (
    SELECT
        COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
        COUNT(DISTINCT o.order_id)                                                    AS orders,
        COUNT(*)                                                                      AS units,
        ROUND(SUM(oi.price), 2)                                                       AS revenue
    FROM orders o
    JOIN customers   c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id  = o.order_id
    JOIN products    p ON p.product_id  = oi.product_id
    LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name
    WHERE o.order_status = 'delivered'
    /*FILTERS*/
    GROUP BY category
)
SELECT
    RANK() OVER (ORDER BY revenue DESC)                                   AS rank_no,
    category, orders, units, revenue,
    ROUND(revenue * 1.0 / units, 2)                                       AS avg_price,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2)                      AS revenue_share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(revenue) OVER (), 2)                                      AS cumulative_share_pct
FROM cat
ORDER BY revenue DESC;

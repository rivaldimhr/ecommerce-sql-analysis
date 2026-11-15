-- Kinerja kategori: GMV, pangsa, pangsa kumulatif (Pareto), rating, keterlambatan,
-- dan persen pembeli yang kembali (pelanggan yang belanja lagi di kategori apa pun).
WITH valid_items AS (
  SELECT i.*, o.customer, o.review_score, o.delay_days, o.status, o.delivered_at
  FROM f_items i JOIN f_orders o USING (order_id)
  WHERE o.is_valid
),
cust_orders AS (SELECT customer, COUNT(*) AS n FROM f_orders WHERE is_valid GROUP BY customer),
cat AS (
  SELECT category,
         COUNT(DISTINCT order_id)                    AS orders,
         SUM(price)                                  AS gmv,
         AVG(price)                                  AS avg_price,
         AVG(freight_value / NULLIF(price, 0))       AS freight_ratio
  FROM valid_items GROUP BY category
),
cat_orders AS (   -- satu baris per (kategori, pesanan) supaya rating tidak terhitung ganda
  SELECT DISTINCT category, order_id, customer, review_score, delay_days, status, delivered_at
  FROM valid_items
),
cat_quality AS (
  SELECT category,
         AVG(review_score) AS avg_review,
         AVG(CASE WHEN status = 'delivered' AND delivered_at IS NOT NULL THEN delay_days > 0 END) AS late_rate
  FROM cat_orders
  GROUP BY category
),
cat_repeat AS (   -- per pelanggan, bukan per pesanan, supaya pelanggan yang sering belanja tidak terhitung ganda
  SELECT cc.category, AVG(co.n > 1) AS repeat_rate
  FROM (SELECT DISTINCT category, customer FROM cat_orders) cc
  JOIN cust_orders co USING (customer)
  GROUP BY cc.category
)
SELECT c.category,
       c.orders,
       ROUND(c.gmv, 2)                                   AS gmv,
       ROUND(100.0 * c.gmv / SUM(c.gmv) OVER (), 2)      AS gmv_pct,
       ROUND(100.0 * SUM(c.gmv) OVER (ORDER BY c.gmv DESC ROWS UNBOUNDED PRECEDING) / SUM(c.gmv) OVER (), 2) AS cum_gmv_pct,
       ROUND(c.avg_price, 2)                             AS avg_price,
       ROUND(100.0 * c.freight_ratio, 1)                 AS freight_pct_of_price,
       ROUND(q.avg_review, 2)                            AS avg_review,
       ROUND(100.0 * q.late_rate, 1)                     AS late_pct,
       ROUND(100.0 * rp.repeat_rate, 2)                  AS repeat_customer_pct
FROM cat c JOIN cat_quality q USING (category) JOIN cat_repeat rp USING (category)
ORDER BY c.gmv DESC;

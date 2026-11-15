-- Semua penjual aktif (>= 50 pesanan terkirim), diurutkan dari yang paling sering terlambat.
-- Dampak = berapa banyak pesanan terlambat yang mereka hasilkan.
WITH s AS (
  SELECT i.seller_id,
         se.seller_state,
         COUNT(DISTINCT o.order_id)                          AS delivered_orders,
         COUNT(DISTINCT CASE WHEN o.delay_days > 0 THEN o.order_id END) AS late_orders,
         AVG(o.review_score)                                 AS avg_review,
         SUM(i.price)                                        AS gmv
  FROM f_items i
  JOIN v_delivered o USING (order_id)
  JOIN sellers se USING (seller_id)
  GROUP BY i.seller_id, se.seller_state
)
SELECT substr(seller_id, 1, 8)                         AS seller,
       seller_state,
       delivered_orders,
       late_orders,
       ROUND(100.0 * late_orders / delivered_orders, 1) AS late_pct,
       ROUND(avg_review, 2)                             AS avg_review,
       ROUND(gmv, 2)                                    AS gmv
FROM s
WHERE delivered_orders >= 50
ORDER BY late_pct DESC, late_orders DESC;

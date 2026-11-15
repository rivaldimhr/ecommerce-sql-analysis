-- Konsentrasi penjual dan penjual bermasalah.
-- Desil penjual menurut GMV; persen GMV, keterlambatan dan rating per desil.
WITH s AS (
  SELECT i.seller_id,
         SUM(i.price)                    AS gmv,
         COUNT(DISTINCT i.order_id)      AS orders,
         AVG(CASE WHEN o.status = 'delivered' AND o.delivered_at IS NOT NULL THEN o.delay_days > 0 END) AS late_rate,
         AVG(o.review_score)             AS avg_review
  FROM f_items i JOIN f_orders o USING (order_id)
  WHERE o.is_valid
  GROUP BY i.seller_id
),
d AS (SELECT *, NTILE(10) OVER (ORDER BY gmv DESC) AS decile FROM s)
SELECT decile,
       COUNT(*)                                          AS sellers,
       SUM(orders)                                       AS orders,
       ROUND(100.0 * SUM(gmv) / SUM(SUM(gmv)) OVER (), 2) AS gmv_pct,
       ROUND(100.0 * SUM(late_rate * orders) / SUM(orders), 1) AS late_pct,
       ROUND(SUM(avg_review * orders) / SUM(orders), 2)  AS avg_review
FROM d
GROUP BY decile
ORDER BY decile;

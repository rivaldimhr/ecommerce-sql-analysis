-- Kinerja per negara bagian pembeli: lama kirim, keterlambatan, ongkir, rating.
SELECT state,
       COUNT(*)                                      AS orders,
       ROUND(SUM(items_value), 2)                    AS gmv,
       ROUND(AVG(delivery_days), 1)                  AS avg_delivery_days,
       ROUND(100.0 * AVG(delay_days > 0), 1)         AS late_pct,
       ROUND(100.0 * SUM(freight_value) / SUM(items_value), 1) AS freight_pct_of_value,
       ROUND(AVG(review_score), 2)                   AS avg_review
FROM v_delivered
GROUP BY state
HAVING COUNT(*) >= 100
ORDER BY orders DESC;

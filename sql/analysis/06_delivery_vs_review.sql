-- Hubungan ketepatan pengiriman dengan rating.
-- delay_days < 0 = tiba sebelum estimasi.
SELECT CASE
         WHEN delay_days <= -8 THEN '1. Lebih cepat > 7 hari'
         WHEN delay_days <= 0  THEN '2. Lebih cepat 0-7 hari'
         WHEN delay_days <= 3  THEN '3. Terlambat 1-3 hari'
         WHEN delay_days <= 7  THEN '4. Terlambat 4-7 hari'
         ELSE                       '5. Terlambat > 7 hari'
       END AS bucket,
       COUNT(*)                                       AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS orders_pct,
       ROUND(AVG(review_score), 2)                    AS avg_review,
       ROUND(100.0 * AVG(review_score <= 2), 1)       AS bad_review_pct,
       ROUND(100.0 * AVG(review_score = 5), 1)        AS five_star_pct
FROM v_delivered
WHERE review_score IS NOT NULL
GROUP BY bucket
ORDER BY bucket;

-- Tren bulanan: pesanan, GMV, pelanggan baru vs pelanggan lama, dan persen terlambat.
WITH valid AS (SELECT * FROM f_orders WHERE is_valid),
first_month AS (SELECT customer, MIN(month) AS first_month FROM valid GROUP BY customer)
SELECT v.month,
       COUNT(*)                                           AS orders,
       ROUND(SUM(v.items_value), 2)                       AS gmv,
       COUNT(DISTINCT CASE WHEN v.month = f.first_month THEN v.customer END) AS new_customers,
       COUNT(DISTINCT CASE WHEN v.month > f.first_month THEN v.customer END) AS returning_customers,
       ROUND(100.0 * AVG(CASE WHEN v.status = 'delivered' AND v.delivered_at IS NOT NULL
                              THEN v.delay_days > 0 END), 1) AS late_pct,
       ROUND(AVG(v.review_score), 2)                      AS avg_review
FROM valid v
JOIN first_month f USING (customer)
GROUP BY v.month
ORDER BY v.month;

-- Mana yang lebih menentukan rating: lama kirim, atau janji (estimasi) ditepati?
-- Rating dibandingkan per kelompok lama kirim, dipisah tepat waktu vs terlambat.
SELECT CASE
         WHEN delivery_days <= 7  THEN '1. s.d. 7 hari'
         WHEN delivery_days <= 14 THEN '2. 8-14 hari'
         WHEN delivery_days <= 21 THEN '3. 15-21 hari'
         ELSE                          '4. lebih dari 21 hari'
       END AS delivery_time,
       ROUND(AVG(CASE WHEN delay_days <= 0 THEN review_score END), 2) AS review_on_time,
       SUM(delay_days <= 0)                                             AS orders_on_time,
       ROUND(AVG(CASE WHEN delay_days > 0 THEN review_score END), 2)  AS review_late,
       SUM(delay_days > 0)                                              AS orders_late
FROM v_delivered
WHERE review_score IS NOT NULL
GROUP BY delivery_time
ORDER BY delivery_time;

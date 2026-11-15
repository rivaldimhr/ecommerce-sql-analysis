-- Retensi per cohort: dari pelanggan yang pertama belanja di bulan X,
-- berapa persen yang belanja lagi k bulan kemudian (k = 1..6).
WITH valid AS (SELECT customer, month FROM f_orders WHERE is_valid),
first_month AS (SELECT customer, MIN(month) AS cohort FROM valid GROUP BY customer),
activity AS (
  SELECT DISTINCT f.cohort,
         v.customer,
         (CAST(substr(v.month, 1, 4) AS INTEGER) - CAST(substr(f.cohort, 1, 4) AS INTEGER)) * 12
       + (CAST(substr(v.month, 6, 2) AS INTEGER) - CAST(substr(f.cohort, 6, 2) AS INTEGER)) AS k
  FROM valid v JOIN first_month f USING (customer)
),
size AS (SELECT cohort, COUNT(*) AS customers FROM first_month GROUP BY cohort)
SELECT s.cohort,
       s.customers,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 1 THEN a.customer END) / s.customers, 2) AS m1,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 2 THEN a.customer END) / s.customers, 2) AS m2,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 3 THEN a.customer END) / s.customers, 2) AS m3,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 4 THEN a.customer END) / s.customers, 2) AS m4,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 5 THEN a.customer END) / s.customers, 2) AS m5,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 6 THEN a.customer END) / s.customers, 2) AS m6,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k BETWEEN 1 AND 6 THEN a.customer END) / s.customers, 2) AS within_6m,
       -- bulan cohort ditambah k yang masih di dalam periode data (s.d. 2018-08)
       (2018 - CAST(substr(s.cohort, 1, 4) AS INTEGER)) * 12 + (8 - CAST(substr(s.cohort, 6, 2) AS INTEGER)) AS months_observed
FROM size s
LEFT JOIN activity a USING (cohort)
GROUP BY s.cohort
ORDER BY s.cohort;

-- Segmentasi RFM per pelanggan, tanggal acuan 2018-09-01.
-- R dan M dibagi 5 kelompok (NTILE). F tidak dibagi rata karena 97% pelanggan
-- hanya belanja sekali; F diberi skor 1 (sekali), 4 (dua kali), 5 (tiga kali atau lebih).
WITH valid AS (SELECT * FROM f_orders WHERE is_valid AND item_count > 0),
base AS (
  SELECT customer,
         CAST(julianday('2018-09-01') - julianday(MAX(purchased_at)) AS INTEGER) AS recency_days,
         COUNT(*)          AS frequency,
         SUM(items_value)  AS monetary
  FROM valid
  GROUP BY customer
),
scored AS (
  SELECT *,
         6 - NTILE(5) OVER (ORDER BY recency_days) AS r,
         CASE WHEN frequency >= 3 THEN 5 WHEN frequency = 2 THEN 4 ELSE 1 END AS f,
         NTILE(5) OVER (ORDER BY monetary) AS m
  FROM base
),
segmented AS (
  SELECT *,
         CASE
           WHEN f >= 4 AND r >= 4                 THEN 'Champions'
           WHEN f >= 4                            THEN 'Loyal, mulai pasif'
           WHEN r >= 4 AND m >= 4                 THEN 'Baru, nilai tinggi'
           WHEN r >= 4                            THEN 'Baru, nilai rendah'
           WHEN r = 3                             THEN 'Perlu perhatian'
           WHEN m >= 4                            THEN 'Nilai tinggi, hampir hilang'
           ELSE                                        'Hilang'
         END AS segment
  FROM scored
)
SELECT segment,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customers_pct,
       ROUND(SUM(monetary), 2)                         AS gmv,
       ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS gmv_pct,
       ROUND(AVG(recency_days), 0)                     AS avg_recency_days,
       ROUND(AVG(frequency), 2)                        AS avg_frequency,
       ROUND(AVG(monetary), 2)                         AS avg_monetary
FROM segmented
GROUP BY segment
ORDER BY gmv DESC;

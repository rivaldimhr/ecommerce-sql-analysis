-- Apakah pengalaman pertama memengaruhi pembelian berikutnya?
-- Pelanggan dikelompokkan menurut pesanan PERTAMA mereka (terlambat atau tidak, rating),
-- lalu dihitung berapa persen yang belanja lagi. Pesanan pertama dibatasi s.d. Feb 2018
-- supaya setiap pelanggan punya minimal 6 bulan untuk kembali.
WITH valid AS (SELECT * FROM f_orders WHERE is_valid),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer ORDER BY purchased_at, order_id) AS rn,
            COUNT(*)     OVER (PARTITION BY customer) AS n
  FROM valid
),
first_orders AS (
  SELECT * FROM ranked
  WHERE rn = 1 AND purchased_at < '2018-03-01'
    AND status = 'delivered' AND delivered_at IS NOT NULL
)
SELECT 'Pengiriman' AS dimension,
       CASE WHEN delay_days > 0 THEN 'Terlambat' ELSE 'Tepat waktu' END AS first_order,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(n > 1), 2) AS repeat_pct
FROM first_orders GROUP BY 2
UNION ALL
SELECT 'Rating',
       CASE WHEN review_score <= 2 THEN 'Bintang 1-2'
            WHEN review_score = 3  THEN 'Bintang 3'
            ELSE 'Bintang 4-5' END,
       COUNT(*),
       ROUND(100.0 * AVG(n > 1), 2)
FROM first_orders WHERE review_score IS NOT NULL GROUP BY 2
ORDER BY 1, 2;

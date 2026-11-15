-- Pembersihan dan tabel analisis.
-- Aturan (lihat README, bagian "Kualitas data"):
--   * Periode analisis: 2017-01-01 s.d. 2018-08-31. Data 2016 dan Sep-Okt 2018 terlalu sedikit (<350 pesanan/bulan).
--   * Pelanggan = customer_unique_id. customer_id dibuat baru untuk setiap pesanan.
--   * Pesanan "valid" = status bukan canceled / unavailable.
--   * Satu review per pesanan: yang paling akhir dijawab.
--   * Kategori pakai nama Inggris; tanpa kategori -> 'unknown'.
--   * Nilai penjualan (GMV) = jumlah harga barang, tanpa ongkir.

-- Terjemahan yang tidak ada di file resmi
INSERT OR IGNORE INTO category_translation VALUES
  ('pc_gamer', 'pc_gamer'),
  ('portateis_cozinha_e_preparadores_de_alimentos', 'portable_kitchen_food_preparers');

DROP TABLE IF EXISTS f_reviews;
CREATE TABLE f_reviews AS
SELECT order_id, review_score, review_comment_message
FROM (
  SELECT r.*,
         ROW_NUMBER() OVER (PARTITION BY order_id
                            ORDER BY review_answer_timestamp DESC, review_id) AS rn
  FROM order_reviews r
)
WHERE rn = 1;
CREATE UNIQUE INDEX idx_f_reviews ON f_reviews(order_id);

DROP TABLE IF EXISTS f_items;
CREATE TABLE f_items AS
SELECT i.order_id,
       i.order_item_id,
       i.product_id,
       i.seller_id,
       i.price,
       i.freight_value,
       COALESCE(t.product_category_name_english, 'unknown') AS category
FROM order_items i
LEFT JOIN products p USING (product_id)
LEFT JOIN category_translation t USING (product_category_name);
CREATE INDEX idx_f_items_order ON f_items(order_id);

DROP TABLE IF EXISTS f_orders;
CREATE TABLE f_orders AS
WITH items AS (
  SELECT order_id,
         COUNT(*)           AS item_count,
         SUM(price)         AS items_value,
         SUM(freight_value) AS freight_value
  FROM f_items
  GROUP BY order_id
)
SELECT o.order_id,
       c.customer_unique_id                         AS customer,
       c.customer_state                             AS state,
       o.order_status                               AS status,
       o.order_status NOT IN ('canceled', 'unavailable') AS is_valid,
       o.order_purchase_timestamp                   AS purchased_at,
       substr(o.order_purchase_timestamp, 1, 7)     AS month,
       o.order_delivered_customer_date              AS delivered_at,
       o.order_estimated_delivery_date              AS estimated_at,
       ROUND(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp), 2) AS delivery_days,
       -- positif = terlambat dari estimasi, negatif = lebih cepat (dalam hari kalender)
       CAST(julianday(date(o.order_delivered_customer_date)) - julianday(date(o.order_estimated_delivery_date)) AS INTEGER) AS delay_days,
       COALESCE(i.item_count, 0)    AS item_count,
       COALESCE(i.items_value, 0)   AS items_value,
       COALESCE(i.freight_value, 0) AS freight_value,
       r.review_score
FROM orders o
JOIN customers c USING (customer_id)
LEFT JOIN items i USING (order_id)
LEFT JOIN f_reviews r USING (order_id)
WHERE o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01';
CREATE UNIQUE INDEX idx_f_orders ON f_orders(order_id);
CREATE INDEX idx_f_orders_customer ON f_orders(customer);

-- Pesanan valid yang sudah diterima pelanggan: dasar analisis pengiriman
DROP VIEW IF EXISTS v_delivered;
CREATE VIEW v_delivered AS
SELECT * FROM f_orders
WHERE status = 'delivered' AND delivered_at IS NOT NULL;

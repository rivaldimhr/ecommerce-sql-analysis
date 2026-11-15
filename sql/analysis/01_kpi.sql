-- Ringkasan bisnis untuk seluruh periode (Jan 2017 - Agu 2018).
WITH valid AS (SELECT * FROM f_orders WHERE is_valid),
per_customer AS (SELECT customer, COUNT(*) AS n FROM valid GROUP BY customer)
SELECT
  (SELECT COUNT(*) FROM valid)                                   AS orders,
  (SELECT COUNT(*) FROM per_customer)                            AS customers,
  (SELECT ROUND(SUM(items_value), 2) FROM valid)                 AS gmv,
  (SELECT ROUND(AVG(items_value), 2) FROM valid WHERE item_count > 0) AS avg_order_value,
  (SELECT ROUND(100.0 * SUM(n > 1) / COUNT(*), 2) FROM per_customer) AS repeat_customer_pct,
  (SELECT ROUND(AVG(review_score), 2) FROM valid WHERE review_score IS NOT NULL) AS avg_review,
  (SELECT ROUND(100.0 * AVG(delay_days > 0), 2) FROM v_delivered) AS late_pct,
  (SELECT ROUND(AVG(delivery_days), 1) FROM v_delivered)          AS avg_delivery_days,
  (SELECT ROUND(100.0 * SUM(freight_value) / SUM(items_value), 1) FROM valid) AS freight_to_value_pct;

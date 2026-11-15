-- Cara bayar dan cicilan.
WITH p AS (
  SELECT op.*
  FROM order_payments op JOIN f_orders o USING (order_id)
  WHERE o.is_valid AND op.payment_type <> 'not_defined'
)
SELECT payment_type,
       COUNT(DISTINCT order_id)                               AS orders,
       ROUND(100.0 * SUM(payment_value) / SUM(SUM(payment_value)) OVER (), 2) AS value_pct,
       ROUND(AVG(payment_value), 2)                           AS avg_payment,
       ROUND(AVG(CASE WHEN payment_type = 'credit_card' THEN payment_installments END), 2) AS avg_installments
FROM p
GROUP BY payment_type
ORDER BY orders DESC;

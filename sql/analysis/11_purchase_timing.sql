-- Kapan pelanggan berbelanja: hari (0 = Minggu) x jam.
SELECT CAST(strftime('%w', purchased_at) AS INTEGER) AS weekday,
       CAST(strftime('%H', purchased_at) AS INTEGER) AS hour,
       COUNT(*) AS orders
FROM f_orders
WHERE is_valid
GROUP BY weekday, hour
ORDER BY weekday, hour;

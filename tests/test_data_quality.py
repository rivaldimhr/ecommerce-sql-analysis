"""Aturan pembersihan di sql/01_clean.sql benar-benar berlaku."""


def test_raw_tables_loaded_completely(q):
    counts = dict(q("""SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'customers', COUNT(*) FROM customers
                       UNION ALL SELECT 'items', COUNT(*) FROM order_items UNION ALL SELECT 'reviews', COUNT(*) FROM order_reviews"""))
    assert counts == {"orders": 99441, "customers": 99441, "items": 112650, "reviews": 99224}


def test_period_is_jan_2017_to_aug_2018(q):
    lo, hi = q("SELECT MIN(purchased_at), MAX(purchased_at) FROM f_orders")[0]
    assert lo >= "2017-01-01" and hi < "2018-09-01"


def test_one_row_per_order(q):
    assert q("SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM f_orders")[0][0] == 0


def test_one_review_per_order(q):
    assert q("SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM f_reviews")[0][0] == 0
    # pesanan dengan lebih dari satu review memakai yang paling akhir dijawab
    order_id, = q("""SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1 ORDER BY order_id LIMIT 1""")[0]
    latest, = q(f"""SELECT review_score FROM order_reviews WHERE order_id = '{order_id}'
                    ORDER BY review_answer_timestamp DESC, review_id LIMIT 1""")[0]
    assert q(f"SELECT review_score FROM f_reviews WHERE order_id = '{order_id}'")[0][0] == latest


def test_every_order_has_a_real_customer(q):
    assert q("SELECT COUNT(*) FROM f_orders WHERE customer IS NULL")[0][0] == 0


def test_customer_is_unique_person_not_order(q):
    orders, people = q("SELECT COUNT(DISTINCT order_id), COUNT(DISTINCT customer) FROM f_orders")[0]
    assert people < orders


def test_gmv_matches_item_prices(q):
    a = q("SELECT ROUND(SUM(items_value), 2) FROM f_orders WHERE is_valid")[0][0]
    b = q("""SELECT ROUND(SUM(i.price), 2) FROM order_items i JOIN f_orders o USING (order_id) WHERE o.is_valid""")[0][0]
    assert a == b


def test_all_categories_translated(q):
    untranslated = q("""SELECT COUNT(*) FROM products p LEFT JOIN category_translation t USING (product_category_name)
                        WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL""")[0][0]
    assert untranslated == 0
    assert q("SELECT COUNT(*) FROM f_items WHERE category IS NULL")[0][0] == 0


def test_delay_sign(q):
    # tiba sebelum estimasi => delay negatif atau nol
    bad = q("""SELECT COUNT(*) FROM v_delivered
               WHERE date(delivered_at) <= date(estimated_at) AND delay_days > 0""")[0][0]
    assert bad == 0


def test_delivered_view_has_dates(q):
    assert q("SELECT COUNT(*) FROM v_delivered WHERE delivered_at IS NULL OR delivery_days < 0")[0][0] == 0

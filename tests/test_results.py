"""Hasil analisis konsisten satu sama lain (cek silang antar-query)."""
import math

import pytest


def test_kpi_values(data):
    k = data["kpi"][0]
    assert k["orders"] == 97910
    assert k["customers"] == 94707
    assert 2.5 < k["repeat_customer_pct"] < 3.5
    assert 1 <= k["avg_review"] <= 5


def test_monthly_orders_sum_to_kpi(data):
    assert sum(r["orders"] for r in data["monthly"]) == data["kpi"][0]["orders"]
    assert len(data["monthly"]) == 20


def test_new_customers_sum_to_all_customers(data):
    # setiap pelanggan baru tepat sekali, di bulan pertamanya
    assert sum(r["new_customers"] for r in data["monthly"]) == data["kpi"][0]["customers"]


def test_cohorts_match_new_customers(data):
    new = {r["month"]: r["new_customers"] for r in data["monthly"]}
    for c in data["cohort_retention"]:
        assert c["customers"] == new[c["cohort"]]


def test_cohort_cells_after_end_of_data_are_zero(data):
    for c in data["cohort_retention"]:
        for k in range(c["months_observed"] + 1, 7):
            assert c[f"m{k}"] == 0


def test_cohort_retention_is_low(data):
    observed = [c for c in data["cohort_retention"] if c["months_observed"] >= 6]
    assert observed and all(c["within_6m"] < 3 for c in observed)
    assert all(c["m1"] < 1 for c in data["cohort_retention"])


def test_rfm_covers_every_customer_with_items(data, q):
    n = q("SELECT COUNT(DISTINCT customer) FROM f_orders WHERE is_valid AND item_count > 0")[0][0]
    assert sum(r["customers"] for r in data["rfm_segments"]) == n
    assert sum(r["gmv_pct"] for r in data["rfm_segments"]) == pytest.approx(100, abs=0.05)


def test_category_gmv_matches_total(data):
    assert sum(r["gmv"] for r in data["categories"]) == pytest.approx(data["kpi"][0]["gmv"], abs=1)
    assert data["categories"][-1]["cum_gmv_pct"] == pytest.approx(100, abs=0.01)


def test_category_repeat_counts_people_not_orders(q, data):
    # hitung ulang satu kategori secara manual
    cat = "bed_bath_table"
    manual, = q(f"""
        WITH cust AS (SELECT customer, COUNT(*) AS n FROM f_orders WHERE is_valid GROUP BY customer)
        SELECT ROUND(100.0 * AVG(c.n > 1), 2)
        FROM (SELECT DISTINCT o.customer FROM f_items i JOIN f_orders o USING (order_id)
              WHERE o.is_valid AND i.category = '{cat}') x
        JOIN cust c USING (customer)""")[0]
    assert next(r for r in data["categories"] if r["category"] == cat)["repeat_customer_pct"] == manual


def test_delay_buckets_cover_all_reviewed_deliveries(data, q):
    n = q("SELECT COUNT(*) FROM v_delivered WHERE review_score IS NOT NULL")[0][0]
    assert sum(r["orders"] for r in data["delivery_vs_review"]) == n


def test_late_orders_get_worse_reviews(data):
    bad = [r["bad_review_pct"] for r in data["delivery_vs_review"]]
    assert bad[2] < bad[3] < bad[4]           # makin terlambat, makin buruk
    assert max(bad[:2]) < min(bad[2:])        # setiap kelompok terlambat lebih buruk dari yang tepat waktu


def test_promise_matters_more_than_speed(data):
    for r in data["promise_vs_speed"]:
        assert r["review_on_time"] > r["review_late"]


def test_significance_matches_manual_z_test(data):
    rows = {(r["dimension"], r["first_order"]): r for r in data["late_first_order_retention"]}
    a, b = rows[("Pengiriman", "Tepat waktu")], rows[("Pengiriman", "Terlambat")]
    p1, p2 = a["repeat_pct"] / 100, b["repeat_pct"] / 100
    pooled = (p1 * a["customers"] + p2 * b["customers"]) / (a["customers"] + b["customers"])
    z = (p1 - p2) / math.sqrt(pooled * (1 - pooled) * (1 / a["customers"] + 1 / b["customers"]))
    s = next(r for r in data["significance"] if r["dimension"] == "Pengiriman")
    assert s["z"] == pytest.approx(z, abs=0.01)
    assert s["significant"] is True


def test_seller_deciles(data):
    d = data["sellers"]
    assert [r["decile"] for r in d] == list(range(1, 11))
    assert sum(r["gmv_pct"] for r in d) == pytest.approx(100, abs=0.05)
    assert d[0]["gmv_pct"] > 60


def test_problem_sellers_are_all_active_sellers(data):
    ps = data["problem_sellers"]
    assert all(r["delivered_orders"] >= 50 for r in ps)
    assert [r["late_pct"] for r in ps] == sorted((r["late_pct"] for r in ps), reverse=True)


def test_purchase_timing_covers_valid_orders(data):
    assert sum(r["orders"] for r in data["purchase_timing"]) == data["kpi"][0]["orders"]


def test_every_query_has_sql_text(data):
    names = [k for k in data if not k.startswith("_") and k != "significance"]
    assert set(names) <= set(data["_sql"])

"""Dashboard tampil tanpa error dan angka di teks cocok dengan data."""
import re

import pytest

pw = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def open_page(browser, site, width=1280, height=900):
    pg = browser.new_page(viewport={"width": width, "height": height})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    # font Google tidak wajib untuk test; tanpa jaringan permintaannya dibatalkan
    pg.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), lambda r: r.abort())
    pg.goto(site)
    pg.wait_for_selector('body[data-ready="1"]', timeout=15000)
    return pg


@pytest.fixture(scope="module")
def page(browser, site):
    pg = open_page(browser, site)
    yield pg
    pg.close()


def test_no_javascript_errors(page):
    assert page.errors == []


def test_every_sql_block_is_filled(page):
    blocks = page.locator("pre[data-sql]")
    assert blocks.count() >= 12
    for i in range(blocks.count()):
        assert "SELECT" in blocks.nth(i).text_content()


def test_sql_toggle_opens(page):
    d = page.locator("#retensi details.sql").first
    d.locator("summary").click()
    assert d.evaluate("e => e.open")
    assert d.locator("pre").is_visible()


def test_charts_rendered(page):
    for cid in ["hero-chart", "monthly-chart", "rfm-chart", "first-chart", "late-chart", "seller-chart", "time-chart"]:
        assert page.locator(f"#{cid} svg").count() == 1, cid
    assert page.locator("#cohort tbody tr").count() == 19
    assert page.locator("#cat-table tbody tr").count() == 15
    assert page.locator("#recs .rec").count() == 5


def _num(s):
    return float(s.replace(".", "").replace(",", "."))


def test_text_numbers_match_data(page, data):
    k = data["kpi"][0]
    text = page.locator("#retensi .answer").inner_text()
    assert max(c["m1"] for c in data["cohort_retention"]) < 1 and "kurang dari 1%" in text

    text = page.locator("#pengiriman .answer").inner_text()
    worst = data["delivery_vs_review"][-1]
    assert f"{worst['avg_review']:.1f}".replace(".", ",") in text
    assert f"{round(worst['bad_review_pct'])}%" in text
    peak = max(data["monthly"], key=lambda r: r["late_pct"])
    assert peak["month"] == "2018-03"

    text = page.locator("#kategori .answer").inner_text()
    big = sorted((c for c in data["categories"] if c["orders"] >= 1000 and c["category"] != "unknown"),
                 key=lambda c: -c["repeat_customer_pct"])[:3]
    for c in big:
        assert f"{c['repeat_customer_pct']:.1f}".replace(".", ",") + "%" in text, c["category"]
    top15 = data["categories"][14]["cum_gmv_pct"]
    assert 70 <= top15 <= 80 and "tiga perempat" in text

    text = page.locator("#penjual .answer").inner_text()
    lates = [r["late_pct"] for r in data["sellers"]]
    m = re.search(r"sekitar (\d+)–(\d+)%", text)
    assert int(m.group(1)) <= min(lates) and max(lates) <= int(m.group(2)) + 0.5
    assert 60 < data["sellers"][0]["gmv_pct"] < 70 and "dua pertiga" in text

    facts = page.locator("#facts").inner_text()
    assert f"{k['orders']:,}".replace(",", ".") in facts


def test_mobile_has_no_horizontal_scroll(browser, site):
    pg = open_page(browser, site, 390, 844)
    assert pg.evaluate("document.documentElement.scrollWidth") <= 390
    assert pg.errors == []
    pg.close()

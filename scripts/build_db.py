"""Muat CSV Olist ke SQLite, lalu jalankan skrip pembersihan.

Pemakaian: python scripts/build_db.py [folder_csv] [file_db]
"""
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw"
DB = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "olist.db"

FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def load(con, table, path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        cols = ",".join(header)
        marks = ",".join("?" * len(header))
        rows = ([v if v != "" else None for v in r] for r in reader)
        con.executemany(f"INSERT INTO {table} ({cols}) VALUES ({marks})", rows)
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def main():
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "sql" / "00_schema.sql").read_text())
    for table, name in FILES.items():
        n = load(con, table, RAW / name)
        print(f"{table:22s} {n:>8,d} baris")
    con.commit()
    con.executescript((ROOT / "sql" / "01_clean.sql").read_text())
    con.commit()
    con.close()
    print(f"Database siap: {DB}")


if __name__ == "__main__":
    main()

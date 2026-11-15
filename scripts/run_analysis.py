"""Jalankan setiap query di sql/analysis/ dan simpan hasilnya.

Output:
  results/<nama>.csv     satu file per query (mudah dibuka di Excel)
  dashboard/data.json    semua hasil, dibaca oleh dashboard

Pemakaian: python scripts/run_analysis.py [file_db]
"""
import csv
import json
import sqlite3
import sys
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "olist.db"


def run(con, path):
    cur = con.execute(path.read_text())
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()


def two_proportion_z(p1, n1, p2, n2):
    """Uji z dua proporsi (p dalam persen). Mengembalikan (z, p-value dua sisi)."""
    a, b = p1 / 100, p2 / 100
    pooled = (a * n1 + b * n2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (a - b) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def significance(rows):
    """Bandingkan setiap kelompok pesanan pertama dengan kelompok terbaiknya."""
    reference = {"Pengiriman": "Tepat waktu", "Rating": "Bintang 4-5"}
    ref = {r["dimension"]: r for r in rows if r["first_order"] == reference[r["dimension"]]}
    out = []
    for r in rows:
        base = ref[r["dimension"]]
        if r is base:
            continue
        z, pval = two_proportion_z(base["repeat_pct"], base["customers"], r["repeat_pct"], r["customers"])
        out.append({
            "dimension": r["dimension"],
            "group": r["first_order"],
            "reference": base["first_order"],
            "repeat_pct": r["repeat_pct"],
            "reference_repeat_pct": base["repeat_pct"],
            "relative_drop_pct": round(100 * (1 - r["repeat_pct"] / base["repeat_pct"]), 1),
            "z": round(z, 2),
            "p_value": round(pval, 4),
            "significant": pval < 0.05,
        })
    return out


def main():
    con = sqlite3.connect(DB)
    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    data = {"_sql": {}}
    for path in sorted((ROOT / "sql" / "analysis").glob("*.sql")):
        t = time.perf_counter()
        cols, rows = run(con, path)
        name = path.stem.split("_", 1)[1]
        with open(out_dir / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        data[name] = [dict(zip(cols, r)) for r in rows]
        data["_sql"][name] = path.read_text().strip()
        print(f"{path.name:36s} {len(rows):>4d} baris  {time.perf_counter() - t:5.2f}s")
    data["significance"] = significance(data["late_first_order_retention"])
    for r in data["significance"]:
        print(f"  {r['dimension']}: {r['group']} vs {r['reference']}  z={r['z']}  p={r['p_value']}")
    (ROOT / "dashboard" / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print("Hasil disimpan di results/ dan dashboard/data.json")


if __name__ == "__main__":
    main()

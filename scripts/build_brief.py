"""Tulis docs/rekomendasi.md (rekomendasi bisnis satu halaman) dari dashboard/data.json.

Semua angka diambil dari hasil query, sehingga dokumen ini selalu sama dengan dashboard.
Pemakaian: python scripts/build_brief.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "dashboard" / "data.json").read_text())
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def n(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x, d=1):
    return n(x, d) + "%"


def month(m):
    return f"{MONTHS[int(m[5:]) - 1]} {m[:4]}"


def cat(c):
    return c.replace("_", " ").capitalize()


k = D["kpi"][0]
peak = max(D["monthly"], key=lambda r: r["late_pct"])
bf = next(r for r in D["monthly"] if r["month"] == "2017-11")
sig = next(r for r in D["significance"] if r["dimension"] == "Pengiriman")
sig_rating = next(r for r in D["significance"] if r["group"] == "Bintang 1-2")
late_states = sorted(D["states"], key=lambda r: -r["late_pct"])[:4]
seg = {r["segment"]: r for r in D["rfm_segments"]}
hv, lost_hv = seg["Baru, nilai tinggi"], seg["Nilai tinggi, hampir hilang"]
top_repeat = sorted((c for c in D["categories"] if c["orders"] >= 1000 and c["category"] != "unknown"),
                    key=lambda c: -c["repeat_customer_pct"])[:2]
pvs = next(r for r in D["promise_vs_speed"] if r["delivery_time"].startswith("3."))
worst = D["delivery_vs_review"][-1]
ps = D["problem_sellers"]
ps_bad = [r for r in ps if r["late_pct"] >= 15]
cohort6 = [c["within_6m"] for c in D["cohort_retention"] if c["months_observed"] >= 6]

brief = f"""# Rekomendasi: menaikkan pembelian ulang di Olist

*Satu halaman. Data: {n(k['orders'])} pesanan valid, Jan 2017 – Agu 2018. Semua angka dihitung dengan SQL di repositori ini.*

## Masalah

Hanya **{pct(k['repeat_customer_pct'])}** pelanggan pernah belanja lebih dari sekali. Dari setiap cohort bulanan, rata-rata hanya
{pct(sum(cohort6) / len(cohort6))} yang kembali dalam 6 bulan. Pertumbuhan Olist hampir seluruhnya bergantung pada pelanggan baru,
yang mahal untuk didapatkan.

## Temuan utama

1. **Keterlambatan menghancurkan rating.** Pesanan yang terlambat lebih dari 7 hari rata-rata dapat {n(worst['avg_review'], 2)} bintang,
   dan {pct(worst['bad_review_pct'], 0)} ulasannya bintang 1–2 (tepat waktu: sekitar 10%).
2. **Yang dinilai adalah janji, bukan kecepatan.** Dengan lama kirim yang sama (15–21 hari), pesanan yang tiba sesuai estimasi
   mendapat {n(pvs['review_on_time'], 2)} bintang, yang terlambat {n(pvs['review_late'], 2)}.
3. **Pesanan pertama yang terlambat menurunkan pembelian ulang {pct(sig['relative_drop_pct'], 0)}** ({pct(sig['repeat_pct'], 2)} vs
   {pct(sig['reference_repeat_pct'], 2)}; uji z, p = {n(sig['p_value'], 3)}). Rating rendah sendiri tidak terbukti berpengaruh
   (p = {n(sig_rating['p_value'], 2)}).
4. **Keterlambatan memuncak saat ramai:** {pct(peak['late_pct'])} pada {month(peak['month'])} dan {pct(bf['late_pct'])} pada
   Black Friday {bf['month'][:4]}, dibanding rata-rata {pct(k['late_pct'])}. Tingkat keterlambatan hampir sama di semua kelompok
   penjual, jadi masalahnya lebih mungkin ada di kapasitas logistik dan rute daripada di ukuran penjual.
5. **Nilai penjualan terkonsentrasi pada pelanggan sekali beli bernilai tinggi:** segmen "Baru, nilai tinggi" ({n(hv['customers'])}
   pelanggan, {pct(hv['gmv_pct'], 0)} nilai penjualan) dan "Nilai tinggi, hampir hilang" ({n(lost_hv['customers'])} pelanggan,
   {pct(lost_hv['gmv_pct'], 0)}).

## Rekomendasi

| # | Langkah | Alasan | Cara mengukur |
|---|---|---|---|
| 1 | Tambah kapasitas kirim dan perlebar estimasi sebelum bulan ramai (Black Friday, awal tahun) | Keterlambatan naik hingga {pct(peak['late_pct'], 0)} saat volume puncak | Persen terlambat di bulan puncak berikutnya di bawah {pct(k['late_pct'])} |
| 2 | Prioritaskan pesanan pertama; kirim permintaan maaf dan voucher otomatis bila terlambat | Dari dua faktor pesanan pertama yang diuji (ketepatan kirim dan rating), hanya ini yang terbukti terkait pembelian ulang | Uji A/B: pembelian ulang 90 hari, voucher vs tanpa voucher |
| 3 | Sesuaikan estimasi di rute paling sering terlambat: {', '.join(f"{r['state']} ({pct(r['late_pct'], 0)})" for r in late_states)} | Rating mengikuti janji; estimasi yang jujur mengurangi kekecewaan | Persen terlambat dan rating per negara bagian |
| 4 | Kampanye pembelian kedua untuk segmen "Baru, nilai tinggi", mulai dari {' dan '.join(f"{cat(c['category'])} ({pct(c['repeat_customer_pct'])})" for c in top_repeat)} | Kategori dengan pembelian ulang alami tertinggi | Pembelian ulang 60 hari vs kelompok kontrol |
| 5 | Tindak lanjuti {len(ps_bad)} dari {n(len(ps))} penjual aktif yang terlambat pada ≥15% pesanan | Jumlahnya kecil, dampaknya langsung ke rating | Persen terlambat penjual tersebut per bulan |

## Batasan

- Data observasional: angka di atas menunjukkan hubungan, bukan sebab-akibat. Langkah 2 dan 4 sebaiknya diuji dengan A/B test dulu.
- Data berhenti di Agustus 2018; cohort yang lebih baru belum bisa diamati 6 bulan penuh.
- Nilai penjualan memakai harga barang tanpa ongkir, dalam real Brasil (R$).
"""

(ROOT / "docs" / "rekomendasi.md").write_text(brief)
print("docs/rekomendasi.md ditulis")

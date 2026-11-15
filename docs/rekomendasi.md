# Rekomendasi: menaikkan pembelian ulang di Olist

*Satu halaman. Data: 97.910 pesanan valid, Jan 2017 – Agu 2018. Semua angka dihitung dengan SQL di repositori ini.*

## Masalah

Hanya **3,0%** pelanggan pernah belanja lebih dari sekali. Dari setiap cohort bulanan, rata-rata hanya
1,8% yang kembali dalam 6 bulan. Pertumbuhan Olist hampir seluruhnya bergantung pada pelanggan baru,
yang mahal untuk didapatkan.

## Temuan utama

1. **Keterlambatan menghancurkan rating.** Pesanan yang terlambat lebih dari 7 hari rata-rata dapat 1,70 bintang,
   dan 79% ulasannya bintang 1–2 (tepat waktu: sekitar 10%).
2. **Yang dinilai adalah janji, bukan kecepatan.** Dengan lama kirim yang sama (15–21 hari), pesanan yang tiba sesuai estimasi
   mendapat 4,18 bintang, yang terlambat 2,91.
3. **Pesanan pertama yang terlambat menurunkan pembelian ulang 25%** (3,05% vs
   4,09%; uji z, p = 0,002). Rating rendah sendiri tidak terbukti berpengaruh
   (p = 0,16).
4. **Keterlambatan memuncak saat ramai:** 19,0% pada Mar 2018 dan 12,4% pada
   Black Friday 2017, dibanding rata-rata 6,8%. Tingkat keterlambatan hampir sama di semua kelompok
   penjual, jadi masalahnya lebih mungkin ada di kapasitas logistik dan rute daripada di ukuran penjual.
5. **Nilai penjualan terkonsentrasi pada pelanggan sekali beli bernilai tinggi:** segmen "Baru, nilai tinggi" (14.664
   pelanggan, 29% nilai penjualan) dan "Nilai tinggi, hampir hilang" (13.984 pelanggan,
   29%).

## Rekomendasi

| # | Langkah | Alasan | Cara mengukur |
|---|---|---|---|
| 1 | Tambah kapasitas kirim dan perlebar estimasi sebelum bulan ramai (Black Friday, awal tahun) | Keterlambatan naik hingga 19% saat volume puncak | Persen terlambat di bulan puncak berikutnya di bawah 6,8% |
| 2 | Prioritaskan pesanan pertama; kirim permintaan maaf dan voucher otomatis bila terlambat | Dari dua faktor pesanan pertama yang diuji (ketepatan kirim dan rating), hanya ini yang terbukti terkait pembelian ulang | Uji A/B: pembelian ulang 90 hari, voucher vs tanpa voucher |
| 3 | Sesuaikan estimasi di rute paling sering terlambat: AL (22%), MA (18%), SE (15%), PI (14%) | Rating mengikuti janji; estimasi yang jujur mengurangi kekecewaan | Persen terlambat dan rating per negara bagian |
| 4 | Kampanye pembelian kedua untuk segmen "Baru, nilai tinggi", mulai dari Fashion bags accessories (8,9%) dan Furniture decor (7,2%) | Kategori dengan pembelian ulang alami tertinggi | Pembelian ulang 60 hari vs kelompok kontrol |
| 5 | Tindak lanjuti 19 dari 424 penjual aktif yang terlambat pada ≥15% pesanan | Jumlahnya kecil, dampaknya langsung ke rating | Persen terlambat penjual tersebut per bulan |

## Batasan

- Data observasional: angka di atas menunjukkan hubungan, bukan sebab-akibat. Langkah 2 dan 4 sebaiknya diuji dengan A/B test dulu.
- Data berhenti di Agustus 2018; cohort yang lebih baru belum bisa diamati 6 bulan penuh.
- Nilai penjualan memakai harga barang tanpa ongkir, dalam real Brasil (R$).

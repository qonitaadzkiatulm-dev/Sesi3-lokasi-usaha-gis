# SPK Pemilihan Lokasi Usaha Menggunakan GIS (SAW & TOPSIS)

Studi kasus mata kuliah: **Informatics Practitioner Lecture Series 2026**
Materi: *Career and Competition in Industrial Era with GIS* (Widi Primadepa, alumni Informatika UNIB).

## 1. Latar Belakang
Pada materi disampaikan bahwa GIS dipakai di hampir semua sektor, salah satunya penentuan lokasi
gerai ritel (contoh: Indomaret menentukan lokasi dan radius gerai berdasarkan populasi, jarak antar
gerai, dan efisiensi logistik). Pemateri juga menekankan bahwa lulusan Informatika punya nilai lebih
karena bisa menjadi *user* sekaligus *developer* GIS, serta menyarankan **Python, GeoPandas, QGIS,
dan PostGIS** (open source) sebagai skill utama. Studi kasus ini menerapkan hal tersebut pada
masalah **pemilihan lokasi minimarket/usaha kecil**.

## 2. Tujuan
Membandingkan alternatif lokasi usaha berdasarkan aksesibilitas, kepadatan penduduk, jarak terhadap
pesaing, dan kriteria lain, lalu membandingkan hasil peringkat metode **SAW** dan **TOPSIS**.

## 3. Data (SINTETIS)
> Dataset dibuat otomatis (`src/generate_data.py`, seed tetap) di sekitar Kota Bengkulu hanya untuk
> demonstrasi. Hasil **bukan rekomendasi bisnis nyata**.

| Layer | Isi | Sumber data nyata yang disarankan |
|---|---|---|
| `kandidat_lokasi.csv` | 10 titik kandidat + harga sewa | survei / listing properti |
| `pesaing.csv` | 18 minimarket eksisting | survei lapangan / Google Maps |
| `zona_penduduk.geojson` | 6 zona + kepadatan (jiwa/km²) | BPS, batas wilayah BIG |
| `jalan_utama.geojson` | 2 ruas jalan | OpenStreetMap / BIG |
| `pusat_keramaian.csv` | kampus, pasar, pusat perbelanjaan | OpenStreetMap |

## 4. Kriteria dan Bobot
| Kode | Kriteria | Tipe | Bobot | Cara hitung (GIS) |
|---|---|---|---|---|
| C1 | Kepadatan penduduk | Benefit | 0.25 | *spatial join* titik ke poligon zona |
| C2 | Jarak ke jalan utama (aksesibilitas) | Cost | 0.20 | jarak titik ke garis |
| C3 | Jarak ke pesaing terdekat | Benefit | 0.20 | jarak titik ke titik terdekat |
| C4 | Jumlah pesaing radius 500 m | Cost | 0.10 | *buffer* + *within* |
| C5 | Jarak ke pusat keramaian | Cost | 0.15 | jarak titik ke titik terdekat |
| C6 | Harga sewa (juta/tahun) | Cost | 0.10 | atribut |

Seluruh perhitungan jarak memakai CRS metrik **EPSG:32748 (UTM 48S)**, bukan derajat.
Bobot bersifat asumsi dan dapat diganti (misal dengan AHP atau wawancara pelaku usaha).

## 5. Metode
- **SAW**: normalisasi benefit `x/max`, cost `min/x`, skor = Σ(bobot × nilai normalisasi).
- **TOPSIS**: normalisasi vektor, pembobotan, solusi ideal positif/negatif, nilai preferensi
  `D-/(D+ + D-)`.
- Perbandingan: korelasi Spearman antar skor dan irisan Top-3.

## 6. Cara Menjalankan
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.generate_data     # (opsional) membuat ulang data sintetis
python main.py                  # hitung kriteria, SAW, TOPSIS, peta, grafik
pytest                          # uji unit SAW/TOPSIS
```
Output di folder `output/`: `hasil_peringkat.csv`, `perbandingan_skor.png`, `peta_lokasi.html`
(buka di browser).

## 7. Hasil (data sintetis, seed 42)
| Kandidat | Zona | Rank SAW | Rank TOPSIS |
|---|---|---|---|
| L05 | B | 3 | **1** |
| L08 | E | **1** | 2 |
| L03 | D | 6 | 3 |
| L06 | C | 2 | 8 |

- Korelasi Spearman SAW vs TOPSIS = **0.624** (sedang).
- Top-3 SAW: L05, L06, L08. Top-3 TOPSIS: L03, L05, L08. Irisan: **L05 dan L08**.

## 8. Analisis
- **L05 dan L08** konsisten masuk Top-3 di kedua metode, sehingga paling kuat sebagai rekomendasi.
  L05 unggul di kepadatan penduduk tinggi, dekat jalan utama, tanpa pesaing dalam 500 m, dan sewa
  murah. L08 sangat dekat pusat keramaian.
- **L06** berada di zona terpadat (9.500 jiwa/km²) sehingga SAW menempatkannya peringkat 2, tetapi
  jaraknya ke jalan utama paling jauh (±3,4 km) sehingga TOPSIS menurunkannya ke peringkat 8.
  Perbedaan ini terjadi karena TOPSIS lebih sensitif terhadap nilai ekstrem (jarak ke solusi
  ideal/negatif), sedangkan SAW bersifat kompensatoris sederhana (nilai tinggi di satu kriteria
  menutupi kelemahan di kriteria lain).
- Hasil kedua metode sebaiknya dibaca bersama; keputusan akhir perlu survei lapangan.

## 9. Keterbatasan dan Pengembangan
- Data sintetis; kepadatan per zona seragam (tidak per titik); jarak garis lurus, bukan jarak tempuh
  jaringan jalan.
- Bobot ditetapkan subjektif. Pengembangan: AHP, analisis sensitivitas bobot, jarak berbasis
  jaringan jalan (OSMnx), data PostGIS, WebGIS dengan REST API Node.js, dan data nyata BIG/BPS/OSM.

## 10. Struktur Proyek
```
.
├── data/            # layer spasial (sintetis)
├── src/
│   ├── generate_data.py   # pembuat data sintetis
│   ├── spatial.py         # ekstraksi kriteria dengan GeoPandas
│   └── mcdm.py            # SAW & TOPSIS
├── tests/test_mcdm.py
├── output/          # hasil: csv, grafik, peta interaktif
├── main.py
└── requirements.txt
```

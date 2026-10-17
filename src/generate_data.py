"""Membuat dataset SINTETIS di sekitar Kota Bengkulu untuk simulasi.

Data ini hanya untuk demonstrasi metode. Untuk penelitian sebenarnya, ganti dengan
data resmi: batas wilayah & DEM (BIG), kepadatan penduduk (BPS), jalan & POI
(OpenStreetMap), lokasi pesaing (survei lapangan / Google Maps).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
rng = np.random.default_rng(42)

LON0, LON1 = 102.22, 102.32
LAT0, LAT1 = -3.86, -3.76


def zona_polygons():
    """Grid 3x2 zona (mirip kelurahan) dengan kepadatan penduduk (jiwa/km2)."""
    densitas = [4200, 7800, 9500, 2600, 5600, 3100]
    nama = ["Zona A", "Zona B", "Zona C", "Zona D", "Zona E", "Zona F"]
    xs = np.linspace(LON0, LON1, 4)
    ys = np.linspace(LAT0, LAT1, 3)
    feats, k = [], 0
    for j in range(2):
        for i in range(3):
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            feats.append({
                "type": "Feature",
                "properties": {"zona": nama[k], "kepadatan": densitas[k]},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]},
            })
            k += 1
    return {"type": "FeatureCollection", "features": feats}


def jalan_utama():
    lines = {
        "Jalan Arteri": [[LON0, -3.810], [102.25, -3.805], [102.28, -3.800], [LON1, -3.795]],
        "Jalan Kolektor": [[102.265, LAT0], [102.268, -3.82], [102.270, -3.80], [102.272, LAT1]],
    }
    feats = [{"type": "Feature", "properties": {"nama": n},
              "geometry": {"type": "LineString", "coordinates": c}}
             for n, c in lines.items()]
    return {"type": "FeatureCollection", "features": feats}


def main():
    DATA.mkdir(exist_ok=True)
    (DATA / "zona_penduduk.geojson").write_text(json.dumps(zona_polygons()))
    (DATA / "jalan_utama.geojson").write_text(json.dumps(jalan_utama()))

    # Pusat keramaian (kampus, pasar, pusat perbelanjaan) - titik contoh
    poi = pd.DataFrame({
        "nama": ["Kampus", "Pasar", "Pusat Perbelanjaan"],
        "lon": [102.274, 102.262, 102.285],
        "lat": [-3.769, -3.795, -3.812],
    })
    poi.to_csv(DATA / "pusat_keramaian.csv", index=False)

    # Pesaing (minimarket yang sudah ada)
    n_p = 18
    pesaing = pd.DataFrame({
        "nama": [f"Pesaing-{i+1:02d}" for i in range(n_p)],
        "lon": rng.uniform(LON0 + 0.005, LON1 - 0.005, n_p).round(5),
        "lat": rng.uniform(LAT0 + 0.005, LAT1 - 0.005, n_p).round(5),
    })
    pesaing.to_csv(DATA / "pesaing.csv", index=False)

    # Kandidat lokasi usaha + harga sewa per tahun (juta rupiah)
    n_k = 10
    kandidat = pd.DataFrame({
        "id": [f"L{i+1:02d}" for i in range(n_k)],
        "nama": [f"Kandidat {i+1:02d}" for i in range(n_k)],
        "lon": rng.uniform(LON0 + 0.01, LON1 - 0.01, n_k).round(5),
        "lat": rng.uniform(LAT0 + 0.01, LAT1 - 0.01, n_k).round(5),
        "sewa_juta_per_tahun": rng.integers(18, 70, n_k),
    })
    kandidat.to_csv(DATA / "kandidat_lokasi.csv", index=False)
    print("Data sintetis dibuat di", DATA)


if __name__ == "__main__":
    main()

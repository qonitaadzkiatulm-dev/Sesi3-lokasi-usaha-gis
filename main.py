"""SPK Pemilihan Lokasi Usaha (minimarket) - GIS + SAW & TOPSIS."""
from pathlib import Path

import folium
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.mcdm import saw, topsis
from src.spatial import CRS_GEO, KRITERIA, build_criteria, load_layers

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)


def main():
    layers = load_layers()
    kand = build_criteria(layers)

    cols = list(KRITERIA)
    weights = [KRITERIA[c][1] for c in cols]
    types = [KRITERIA[c][2] for c in cols]
    matrix = kand[cols]

    kand["skor_saw"] = saw(matrix, weights, types)
    kand["skor_topsis"] = topsis(matrix, weights, types)
    kand["rank_saw"] = kand["skor_saw"].rank(ascending=False, method="min").astype(int)
    kand["rank_topsis"] = kand["skor_topsis"].rank(ascending=False, method="min").astype(int)

    hasil = kand.drop(columns="geometry").sort_values("rank_topsis")
    hasil.round(4).to_csv(OUT / "hasil_peringkat.csv", index=False)

    # Perbandingan metode
    spearman = kand["skor_saw"].corr(kand["skor_topsis"], method="spearman")
    top3_saw = set(kand.nsmallest(3, "rank_saw")["id"])
    top3_top = set(kand.nsmallest(3, "rank_topsis")["id"])
    print("=== Matriks kriteria & peringkat ===")
    tampil = ["id", "zona"] + cols + ["skor_saw", "rank_saw", "skor_topsis", "rank_topsis"]
    print(hasil[tampil].round(3).to_string(index=False))
    print(f"\nKorelasi Spearman SAW vs TOPSIS : {spearman:.3f}")
    print(f"Top-3 SAW    : {sorted(top3_saw)}")
    print(f"Top-3 TOPSIS : {sorted(top3_top)}")
    print(f"Irisan Top-3 : {sorted(top3_saw & top3_top)}")

    # Grafik perbandingan skor
    h = hasil.set_index("id")
    ax = h[["skor_saw", "skor_topsis"]].plot(kind="bar", figsize=(9, 4.5))
    ax.set_ylabel("Skor"); ax.set_title("Perbandingan Skor SAW vs TOPSIS")
    plt.xticks(rotation=0); plt.tight_layout()
    plt.savefig(OUT / "perbandingan_skor.png", dpi=150)

    # Peta interaktif
    kg = kand.to_crs(CRS_GEO)
    m = folium.Map(location=[-3.81, 102.27], zoom_start=12, tiles="OpenStreetMap")
    folium.GeoJson(layers["zona"], name="Zona penduduk",
                   style_function=lambda f: {"fillOpacity": 0.12, "weight": 1, "color": "#555"},
                   tooltip=folium.GeoJsonTooltip(["zona", "kepadatan"])).add_to(m)
    folium.GeoJson(layers["jalan"], name="Jalan utama",
                   style_function=lambda f: {"color": "#d35400", "weight": 3}).add_to(m)
    for _, r in layers["pesaing"].iterrows():
        folium.CircleMarker([r.lat, r.lon], radius=4, color="red", fill=True,
                            tooltip=r["nama"]).add_to(m)
    for _, r in layers["keramaian"].iterrows():
        folium.Marker([r.lat, r.lon], icon=folium.Icon(color="purple", icon="star"),
                      tooltip=r["nama"]).add_to(m)
    for _, r in kg.iterrows():
        warna = "green" if r.rank_topsis <= 3 else "blue"
        folium.Marker([r.lat, r.lon], icon=folium.Icon(color=warna, icon="shopping-cart"),
                      popup=(f"<b>{r['id']}</b> ({r.zona})<br>SAW #{r.rank_saw} "
                             f"({r.skor_saw:.3f})<br>TOPSIS #{r.rank_topsis} "
                             f"({r.skor_topsis:.3f})")).add_to(m)
    folium.LayerControl().add_to(m)
    m.save(OUT / "peta_lokasi.html")
    print("\nOutput tersimpan di folder output/")


if __name__ == "__main__":
    main()

"""Ekstraksi kriteria dari data spasial dengan GeoPandas."""
from pathlib import Path

import geopandas as gpd
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
CRS_GEO = "EPSG:4326"
CRS_UTM = "EPSG:32748"  # UTM zona 48S (meter) - mencakup Kota Bengkulu
RADIUS_SAING = 500  # meter


def _points(csv):
    df = pd.read_csv(csv)
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=CRS_GEO)


def load_layers():
    return {
        "kandidat": _points(DATA / "kandidat_lokasi.csv"),
        "pesaing": _points(DATA / "pesaing.csv"),
        "keramaian": _points(DATA / "pusat_keramaian.csv"),
        "zona": gpd.read_file(DATA / "zona_penduduk.geojson").set_crs(CRS_GEO, allow_override=True),
        "jalan": gpd.read_file(DATA / "jalan_utama.geojson").set_crs(CRS_GEO, allow_override=True),
    }


def build_criteria(layers) -> gpd.GeoDataFrame:
    """Hitung 6 kriteria untuk tiap kandidat lokasi."""
    kand = layers["kandidat"].to_crs(CRS_UTM)
    pes = layers["pesaing"].to_crs(CRS_UTM)
    ker = layers["keramaian"].to_crs(CRS_UTM)
    zona = layers["zona"].to_crs(CRS_UTM)
    jalan = layers["jalan"].to_crs(CRS_UTM)

    # C1 kepadatan penduduk: spatial join titik-ke-poligon
    kand = gpd.sjoin(kand, zona[["zona", "kepadatan", "geometry"]], how="left", predicate="within")
    kand = kand.drop(columns="index_right").reset_index(drop=True)

    jalan_union = jalan.geometry.union_all()
    pes_union = pes.geometry.union_all()
    ker_union = ker.geometry.union_all()

    kand["C1_kepadatan"] = kand["kepadatan"]
    # C2 aksesibilitas: jarak ke jalan utama (m)
    kand["C2_jarak_jalan_m"] = kand.geometry.distance(jalan_union)
    # C3 jarak ke pesaing terdekat (m)
    kand["C3_jarak_pesaing_m"] = kand.geometry.distance(pes_union)
    # C4 jumlah pesaing dalam radius 500 m (buffer + within)
    kand["C4_pesaing_500m"] = kand.geometry.apply(
        lambda g: int(pes.within(g.buffer(RADIUS_SAING)).sum()))
    # C5 jarak ke pusat keramaian terdekat (m)
    kand["C5_jarak_keramaian_m"] = kand.geometry.distance(ker_union)
    # C6 harga sewa (juta/tahun)
    kand["C6_sewa"] = kand["sewa_juta_per_tahun"]
    return kand


KRITERIA = {
    # kolom: (nama, bobot, tipe)
    "C1_kepadatan": ("Kepadatan penduduk", 0.25, "benefit"),
    "C2_jarak_jalan_m": ("Jarak ke jalan utama", 0.20, "cost"),
    "C3_jarak_pesaing_m": ("Jarak ke pesaing terdekat", 0.20, "benefit"),
    "C4_pesaing_500m": ("Jumlah pesaing radius 500 m", 0.10, "cost"),
    "C5_jarak_keramaian_m": ("Jarak ke pusat keramaian", 0.15, "cost"),
    "C6_sewa": ("Harga sewa", 0.10, "cost"),
}

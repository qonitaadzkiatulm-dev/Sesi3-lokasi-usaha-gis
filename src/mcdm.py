"""Metode SAW dan TOPSIS (Multi-Criteria Decision Making)."""
import numpy as np
import pandas as pd


def _check(weights, types, n_cols):
    w = np.asarray(weights, dtype=float)
    if len(w) != n_cols or len(types) != n_cols:
        raise ValueError("Jumlah bobot/tipe harus sama dengan jumlah kriteria")
    if not np.isclose(w.sum(), 1.0):
        raise ValueError("Total bobot harus 1")
    if any(t not in ("benefit", "cost") for t in types):
        raise ValueError("Tipe kriteria harus 'benefit' atau 'cost'")
    return w


def saw(matrix: pd.DataFrame, weights, types) -> pd.Series:
    """Simple Additive Weighting.
    benefit: r = x / max(x) ; cost: r = min(x) / x ; skor = sum(w * r)
    """
    w = _check(weights, types, matrix.shape[1])
    r = pd.DataFrame(index=matrix.index, columns=matrix.columns, dtype=float)
    for col, t in zip(matrix.columns, types):
        x = matrix[col].astype(float)
        if t == "benefit":
            r[col] = x / x.max()
        else:
            if (x <= 0).any():  # hindari pembagian nol (mis. 0 pesaing): geser +1
                x = x + 1
            r[col] = x.min() / x
    return (r * w).sum(axis=1).rename("skor_saw")


def topsis(matrix: pd.DataFrame, weights, types) -> pd.Series:
    """TOPSIS: normalisasi vektor, bobot, solusi ideal +/-, nilai preferensi."""
    w = _check(weights, types, matrix.shape[1])
    x = matrix.astype(float).to_numpy()
    denom = np.sqrt((x ** 2).sum(axis=0))
    denom[denom == 0] = 1.0
    norm = x / denom
    v = norm * w
    benefit = np.array([t == "benefit" for t in types])
    ideal_pos = np.where(benefit, v.max(axis=0), v.min(axis=0))
    ideal_neg = np.where(benefit, v.min(axis=0), v.max(axis=0))
    d_pos = np.sqrt(((v - ideal_pos) ** 2).sum(axis=1))
    d_neg = np.sqrt(((v - ideal_neg) ** 2).sum(axis=1))
    pref = d_neg / (d_pos + d_neg)
    return pd.Series(pref, index=matrix.index, name="skor_topsis")

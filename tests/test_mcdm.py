import numpy as np
import pandas as pd
import pytest

from src.mcdm import saw, topsis

M = pd.DataFrame({"benefit": [80, 60, 100], "cost": [20, 10, 40]}, index=["A", "B", "C"])
W, T = [0.6, 0.4], ["benefit", "cost"]


def test_saw_manual():
    # A: 0.6*0.8 + 0.4*(10/20)=0.68 ; B: 0.6*0.6+0.4*1=0.76 ; C: 0.6*1+0.4*0.25=0.70
    s = saw(M, W, T)
    assert s["A"] == pytest.approx(0.68)
    assert s["B"] == pytest.approx(0.76)
    assert s["C"] == pytest.approx(0.70)
    assert s.idxmax() == "B"


def test_topsis_range_and_best():
    s = topsis(M, W, T)
    assert ((s >= 0) & (s <= 1)).all()
    assert s.idxmax() in M.index


def test_invalid_weights():
    with pytest.raises(ValueError):
        saw(M, [0.5, 0.2], T)


def test_cost_with_zero_does_not_crash():
    m = pd.DataFrame({"b": [1, 2], "c": [0, 3]})
    assert np.isfinite(saw(m, [0.5, 0.5], ["benefit", "cost"])).all()

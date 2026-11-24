"""Atributos por repetição (spec 02, FEA-02 e FEA-03)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from reabvision.features.angles import ANGLE_COLUMNS, ANGLE_PAIRS

SEQUENCE_LENGTH = 64


def rep_features(angles: pd.DataFrame, fps: float) -> dict[str, float]:
    """Estatísticas de uma repetição para o Random Forest e para as regras de feedback.

    Para cada ângulo: min, max, range, mean, std, vel_mean, vel_max (graus/s, em módulo).
    Mais: duration (s) e asym_<par> (diferença média |esq - dir|).
    """
    if len(angles) == 0:
        raise ValueError("repetição vazia")
    feats: dict[str, float] = {"duration": len(angles) / fps}
    for col in ANGLE_COLUMNS:
        x = angles[col].to_numpy(dtype=float)
        valid = x[~np.isnan(x)]
        if valid.size == 0:
            for stat in ("min", "max", "range", "mean", "std", "vel_mean", "vel_max"):
                feats[f"{col}_{stat}"] = np.nan
            continue
        vel = np.abs(np.diff(valid)) * fps if valid.size > 1 else np.array([0.0])
        feats[f"{col}_min"] = float(valid.min())
        feats[f"{col}_max"] = float(valid.max())
        feats[f"{col}_range"] = float(valid.max() - valid.min())
        feats[f"{col}_mean"] = float(valid.mean())
        feats[f"{col}_std"] = float(valid.std())
        feats[f"{col}_vel_mean"] = float(vel.mean())
        feats[f"{col}_vel_max"] = float(vel.max())
    for pair, (left, right) in ANGLE_PAIRS.items():
        diff = np.abs(angles[left].to_numpy(float) - angles[right].to_numpy(float))
        feats[f"asym_{pair}"] = float(np.nanmean(diff)) if np.any(~np.isnan(diff)) else np.nan
    return feats


def rep_sequence(angles: pd.DataFrame, length: int = SEQUENCE_LENGTH) -> np.ndarray:
    """Repetição reamostrada para (length, n_ângulos) por interpolação linear (entrada da LSTM).

    NaN são preenchidos por interpolação a partir dos quadros válidos. A normalização
    (z-score com estatísticas do treino) é feita no treino, não aqui.
    """
    values = angles[list(ANGLE_COLUMNS)].to_numpy(dtype=float)
    t_src = np.linspace(0.0, 1.0, len(values))
    t_dst = np.linspace(0.0, 1.0, length)
    out = np.zeros((length, values.shape[1]))
    for j in range(values.shape[1]):
        col = values[:, j]
        ok = ~np.isnan(col)
        if ok.sum() >= 2:
            out[:, j] = np.interp(t_dst, t_src[ok], col[ok])
        elif ok.sum() == 1:
            out[:, j] = col[ok][0]
        else:
            out[:, j] = np.nan
    return out

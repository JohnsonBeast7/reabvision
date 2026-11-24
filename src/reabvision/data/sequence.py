"""Formato canônico das séries de exercício (spec 01)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from reabvision.skeleton import N_JOINTS

TARGET_FPS = 30.0


@dataclass
class Sequence:
    """Uma série (ou uma repetição já segmentada) de um participante em um exercício."""

    dataset: str
    """"uiprmd" | "kimore" | "rehab24" | "own"."""
    subject_id: str
    """Único entre datasets, ex.: "uiprmd_s03"."""
    exercise: str
    """"squat" | "lateral_raise" | "front_raise"."""
    joints: np.ndarray
    """(T, 12, 3) no esqueleto comum; NaN se ausente."""
    fps: float
    label: int | None = None
    """1 = correta, 0 = incorreta (da série inteira), quando existir."""
    rep_labels: list[int] | None = None
    """Rótulo por repetição, quando existir."""
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.joints = np.asarray(self.joints, dtype=float)
        if self.joints.ndim != 3 or self.joints.shape[1:] != (N_JOINTS, 3):
            raise ValueError(f"joints deve ser (T, {N_JOINTS}, 3), recebido {self.joints.shape}")


def resample(joints: np.ndarray, fps_in: float, fps_out: float = TARGET_FPS) -> np.ndarray:
    """Reamostra (T, ...) no tempo por interpolação linear (DAT-09). NaN são interpolados."""
    joints = np.asarray(joints, dtype=float)
    n_in = joints.shape[0]
    if n_in < 2 or fps_in == fps_out:
        return joints.copy()
    duration = (n_in - 1) / fps_in
    n_out = int(round(duration * fps_out)) + 1
    t_in = np.arange(n_in) / fps_in
    t_out = np.arange(n_out) / fps_out
    flat = joints.reshape(n_in, -1)
    out = np.empty((n_out, flat.shape[1]))
    for j in range(flat.shape[1]):
        col = flat[:, j]
        ok = ~np.isnan(col)
        out[:, j] = np.interp(t_out, t_in[ok], col[ok]) if ok.sum() >= 2 else np.nan
    return out.reshape(n_out, *joints.shape[1:])

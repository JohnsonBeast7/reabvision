"""Suavização temporal das articulações (spec 02, POS-04)."""

from __future__ import annotations

import numpy as np


class JointSmoother:
    """Média móvel exponencial por articulação.

    alpha = 1 desliga a suavização; valores menores suavizam mais (e atrasam mais).
    Articulações com NaN no quadro atual mantêm o último valor suavizado.
    """

    def __init__(self, alpha: float = 0.5):
        if not 0 < alpha <= 1:
            raise ValueError("alpha deve estar em (0, 1]")
        self.alpha = alpha
        self._state: np.ndarray | None = None

    def reset(self) -> None:
        self._state = None

    def __call__(self, joints: np.ndarray) -> np.ndarray:
        joints = np.asarray(joints, dtype=float)
        if self._state is None or self._state.shape != joints.shape:
            self._state = joints.copy()
            return self._state.copy()
        new = self.alpha * joints + (1 - self.alpha) * self._state
        # Onde o valor novo é NaN, mantém o anterior; onde o anterior é NaN, usa o novo.
        new = np.where(np.isnan(joints), self._state, new)
        new = np.where(np.isnan(self._state), joints, new)
        self._state = new
        return new.copy()

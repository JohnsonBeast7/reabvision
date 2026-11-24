"""Interface comum dos estimadores de pose (spec 02, POS-01)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass
class PoseResult:
    """Pose de uma pessoa em um quadro, já no esqueleto comum de 12 articulações."""

    joints: np.ndarray
    """(12, 3) coordenadas usadas para os ângulos. Em 2D, z = NaN."""
    image_points: np.ndarray
    """(12, 2) coordenadas em pixels, para desenhar o overlay."""
    visibility: np.ndarray
    """(12,) confiança de cada articulação, 0..1."""
    is_3d: bool


class PoseEstimator(Protocol):
    name: str

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int | None = None) -> PoseResult | None:
        """Estima a pose. Retorna None se nenhuma pessoa for encontrada."""
        ...

    def close(self) -> None: ...

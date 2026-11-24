"""Desenho do esqueleto e do painel sobre o quadro."""

from __future__ import annotations

import unicodedata

import cv2
import numpy as np

from reabvision.pose.base import PoseResult
from reabvision.skeleton import BONES, J

GREEN = (80, 200, 80)
RED = (60, 60, 230)
YELLOW = (40, 200, 230)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)


def draw_skeleton(
    frame: np.ndarray, pose: PoseResult | None, valid: bool, min_vis: float = 0.5
) -> None:
    """Desenha in-place no quadro original (antes de espelhar)."""
    if pose is None:
        return
    color = GREEN if valid else YELLOW
    pts = pose.image_points
    vis = pose.visibility
    for a, b in BONES:
        ia, ib = J[a], J[b]
        if vis[ia] < min_vis or vis[ib] < min_vis:
            continue
        cv2.line(frame, tuple(map(int, pts[ia])), tuple(map(int, pts[ib])), color, 3, cv2.LINE_AA)
    for i, (x, y) in enumerate(pts):
        c = color if vis[i] >= min_vis else GRAY
        cv2.circle(frame, (int(x), int(y)), 5, c, -1, cv2.LINE_AA)


def ascii_text(text: str) -> str:
    """cv2.putText não desenha acentos."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def put_text(
    frame: np.ndarray, text: str, org: tuple[int, int], color=WHITE, scale: float = 0.7
) -> None:
    text = ascii_text(text)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)

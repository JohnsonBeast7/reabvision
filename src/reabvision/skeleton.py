"""Esqueleto comum de 12 articulações e mapeamentos de cada fonte para ele.

A ordem de JOINTS é fixa e usada em todo o projeto (spec 01). "Esquerdo" e
"direito" são sempre do ponto de vista do paciente, não da imagem.
"""

from __future__ import annotations

import numpy as np

JOINTS: tuple[str, ...] = (
    "l_shoulder",
    "r_shoulder",
    "l_elbow",
    "r_elbow",
    "l_wrist",
    "r_wrist",
    "l_hip",
    "r_hip",
    "l_knee",
    "r_knee",
    "l_ankle",
    "r_ankle",
)
N_JOINTS = len(JOINTS)
J = {name: i for i, name in enumerate(JOINTS)}

# Índices de cada fonte, na ordem de JOINTS (spec 02, tabela de mapeamento).
MEDIAPIPE_INDEX: tuple[int, ...] = (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28)
COCO_INDEX: tuple[int, ...] = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
KINECT_V2_NAMES: tuple[str, ...] = (
    "ShoulderLeft",
    "ShoulderRight",
    "ElbowLeft",
    "ElbowRight",
    "WristLeft",
    "WristRight",
    "HipLeft",
    "HipRight",
    "KneeLeft",
    "KneeRight",
    "AnkleLeft",
    "AnkleRight",
)

# Segmentos desenhados no overlay.
BONES: tuple[tuple[str, str], ...] = (
    ("l_shoulder", "r_shoulder"),
    ("l_hip", "r_hip"),
    ("l_shoulder", "l_hip"),
    ("r_shoulder", "r_hip"),
    ("l_shoulder", "l_elbow"),
    ("l_elbow", "l_wrist"),
    ("r_shoulder", "r_elbow"),
    ("r_elbow", "r_wrist"),
    ("l_hip", "l_knee"),
    ("l_knee", "l_ankle"),
    ("r_hip", "r_knee"),
    ("r_knee", "r_ankle"),
)


def select(points: np.ndarray, index: tuple[int, ...]) -> np.ndarray:
    """Seleciona as 12 articulações comuns de um array (n_pontos, d) de uma fonte."""
    points = np.asarray(points)
    if points.shape[0] <= max(index):
        raise ValueError(f"esperado ao menos {max(index) + 1} pontos, recebido {points.shape[0]}")
    return points[list(index)]


def from_named(
    points: dict[str, np.ndarray], names: tuple[str, ...] = KINECT_V2_NAMES
) -> np.ndarray:
    """Monta (12, d) a partir de um dicionário nome -> coordenadas (ex.: Kinect)."""
    missing = [n for n in names if n not in points]
    if missing:
        raise KeyError(f"articulações ausentes: {missing}")
    return np.stack([np.asarray(points[n], dtype=float) for n in names])

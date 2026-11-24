"""Ângulos articulares (spec 02, FEA-01).

O mesmo código é usado no treino (Kinect) e no app (webcam), FEA-04.
Entradas com z = NaN (estimadores 2D) usam só x e y.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from reabvision.skeleton import J

# nome -> (A, B, C): ângulo no vértice B entre BA e BC.
ANGLE_TRIPLETS: dict[str, tuple[str, str, str]] = {
    "knee_l": ("l_hip", "l_knee", "l_ankle"),
    "knee_r": ("r_hip", "r_knee", "r_ankle"),
    "hip_l": ("l_shoulder", "l_hip", "l_knee"),
    "hip_r": ("r_shoulder", "r_hip", "r_knee"),
    "elbow_l": ("l_shoulder", "l_elbow", "l_wrist"),
    "elbow_r": ("r_shoulder", "r_elbow", "r_wrist"),
    "shoulder_l": ("l_hip", "l_shoulder", "l_elbow"),
    "shoulder_r": ("r_hip", "r_shoulder", "r_elbow"),
}
ANGLE_COLUMNS: tuple[str, ...] = (*ANGLE_TRIPLETS, "trunk_tilt")
# Pares esquerdo/direito usados nos atributos de assimetria.
ANGLE_PAIRS: dict[str, tuple[str, str]] = {
    "knee": ("knee_l", "knee_r"),
    "hip": ("hip_l", "hip_r"),
    "elbow": ("elbow_l", "elbow_r"),
    "shoulder": ("shoulder_l", "shoulder_r"),
}


def _as_frames(joints: np.ndarray) -> np.ndarray:
    joints = np.asarray(joints, dtype=float)
    if joints.ndim == 2:
        joints = joints[None]
    if joints.ndim != 3 or joints.shape[1] != len(J) or joints.shape[2] not in (2, 3):
        raise ValueError(f"esperado (T, 12, 2|3), recebido {joints.shape}")
    if joints.shape[2] == 2:
        joints = np.concatenate([joints, np.full((*joints.shape[:2], 1), np.nan)], axis=2)
    # Quadros sem profundidade (z todo NaN) viram 2D com z = 0.
    no_depth = np.all(np.isnan(joints[:, :, 2]), axis=1)
    joints = joints.copy()
    joints[no_depth, :, 2] = 0.0
    return joints


def angle_between(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Ângulo em graus no vértice b, vetorizado sobre a primeira dimensão."""
    ba = a - b
    bc = c - b
    norm = np.linalg.norm(ba, axis=-1) * np.linalg.norm(bc, axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = np.sum(ba * bc, axis=-1) / norm
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))


def trunk_tilt(joints: np.ndarray) -> np.ndarray:
    """Inclinação do tronco em relação ao eixo vertical da câmera, em graus (0 = ereto).

    Usa o valor absoluto do cosseno, então funciona tanto com y para cima (Kinect)
    quanto com y para baixo (imagem, MediaPipe).
    """
    mid_hip = (joints[:, J["l_hip"]] + joints[:, J["r_hip"]]) / 2
    mid_shoulder = (joints[:, J["l_shoulder"]] + joints[:, J["r_shoulder"]]) / 2
    v = mid_shoulder - mid_hip
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = np.abs(v[:, 1]) / np.linalg.norm(v, axis=-1)
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))


def compute_angles(joints: np.ndarray) -> pd.DataFrame:
    """(T, 12, 2|3) ou (12, 2|3) -> DataFrame (T, ANGLE_COLUMNS) em graus."""
    frames = _as_frames(joints)
    data = {
        name: angle_between(frames[:, J[a]], frames[:, J[b]], frames[:, J[c]])
        for name, (a, b, c) in ANGLE_TRIPLETS.items()
    }
    data["trunk_tilt"] = trunk_tilt(frames)
    return pd.DataFrame(data, columns=list(ANGLE_COLUMNS))


def primary_angle(angles: pd.DataFrame, columns: list[str]) -> np.ndarray:
    """Média das colunas do ângulo principal, ignorando NaN."""
    values = angles[columns].to_numpy(dtype=float)
    if not values.size:
        return np.array([])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # linha toda NaN -> NaN
        return np.nanmean(values, axis=1)

"""Loader do UI-PRMD, parte Kinect (spec 01, DAT-03).

Cada arquivo é UMA repetição já segmentada (m<movimento>_s<sujeito>_e<episódio>).
Corretas em "Segmented Movements.zip"; incorretas em "Incorrect Segmented Movements.zip".

Formato (texto, vírgulas, 66 colunas = 22 juntas × 3):
- Positions: a junta 0 (cintura) traz a posição absoluta (cm); as demais trazem o
  deslocamento fixo em relação à junta-pai (comprimento do osso), estilo BVH.
- Angles: rotação local de cada junta em graus, na ordem Y, X, Z.
As posições globais saem por cinemática direta: R_global = R_pai · Ry · Rx · Rz e
p = p_pai + R_global_pai · deslocamento. A convenção YXZ foi validada empiricamente
(é a única que dá joelho 171°→81° no agachamento e ombro 24°→92° na abdução).
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import numpy as np

from reabvision.data.sequence import Sequence, mirror_right_arm
from reabvision.paths import DATA

RAW = DATA / "raw" / "uiprmd"
FPS = 30.0
ZIPS = {1: "Segmented Movements.zip", 0: "Incorrect Segmented Movements.zip"}
MOVEMENTS = {"m01": "squat", "m07": "lateral_raise", "m10": "front_raise"}
# m07 e m10 são feitos só com o braço direito; o app usa os dois braços.
ONE_ARM = {"m07", "m10"}

# Hierarquia das 22 juntas do Kinect no UI-PRMD (pai de cada junta; -1 = raiz).
# 0 cintura, 1 coluna, 2 peito, 3 pescoço, 4 cabeça, 5 topo da cabeça,
# 6-9 clavícula/ombro/cotovelo/punho esq., 10-13 dir., 14-17 quadril/joelho/tornozelo/dedos esq.,
# 18-21 dir.
PARENT = (-1, 0, 1, 2, 3, 4, 2, 6, 7, 8, 2, 10, 11, 12, 0, 14, 15, 16, 0, 18, 19, 20)
# Índices na ordem do esqueleto comum (skeleton.JOINTS).
COMMON_INDEX = (7, 11, 8, 12, 9, 13, 14, 18, 15, 19, 16, 20)
NAME_RE = re.compile(r"(m\d\d)_s(\d\d)_e(\d\d)_(positions|angles)(?:_inc)?\.txt$")


def _rot(axis: str, deg: np.ndarray) -> np.ndarray:
    """Matrizes de rotação (T, 3, 3) em torno de um eixo."""
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    one, zero = np.ones_like(a), np.zeros_like(a)
    if axis == "x":
        m = [[one, zero, zero], [zero, c, -s], [zero, s, c]]
    elif axis == "y":
        m = [[c, zero, s], [zero, one, zero], [-s, zero, c]]
    else:
        m = [[c, -s, zero], [s, c, zero], [zero, zero, one]]
    return np.moveaxis(np.array(m), (0, 1), (-2, -1))


def forward_kinematics(positions: np.ndarray, angles: np.ndarray) -> np.ndarray:
    """(T, 22, 3) deslocamentos + (T, 22, 3) ângulos YXZ -> (T, 22, 3) posições globais."""
    t = positions.shape[0]
    out = np.zeros((t, 22, 3))
    rot_global: list[np.ndarray] = [np.empty(0)] * 22
    for j in range(22):
        local = _rot("y", angles[:, j, 0]) @ _rot("x", angles[:, j, 1]) @ _rot("z", angles[:, j, 2])
        p = PARENT[j]
        if p < 0:
            out[:, j] = positions[:, 0]
            rot_global[j] = local
        else:
            out[:, j] = out[:, p] + np.einsum("tij,tj->ti", rot_global[p], positions[:, j])
            rot_global[j] = rot_global[p] @ local
    return out


def _read(zf: zipfile.ZipFile, name: str) -> np.ndarray:
    data = np.loadtxt(io.StringIO(zf.read(name).decode()), delimiter=",", ndmin=2)
    return data.reshape(len(data), 22, 3)


def load_uiprmd(raw_dir: Path = RAW, movements: dict[str, str] = MOVEMENTS) -> list[Sequence]:
    """Uma Sequence por repetição, em metros, no esqueleto comum."""
    seqs = []
    for label, zip_name in ZIPS.items():
        path = raw_dir / zip_name
        if not path.exists():
            raise FileNotFoundError(f"{path} — rode: python -m reabvision.data.download uiprmd")
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            positions = {
                NAME_RE.search(n).groups()[:3]: n
                for n in names
                if "/Kinect/Positions/" in n and NAME_RE.search(n)
            }
            angles = {
                NAME_RE.search(n).groups()[:3]: n
                for n in names
                if "/Kinect/Angles/" in n and NAME_RE.search(n)
            }
            for key in sorted(positions.keys() & angles.keys()):
                movement, subject, episode = key
                if movement not in movements:
                    continue
                pos = _read(zf, positions[key])
                ang = _read(zf, angles[key])
                n = min(len(pos), len(ang))
                glob = forward_kinematics(pos[:n], ang[:n]) / 100.0  # cm -> m
                joints = glob[:, list(COMMON_INDEX)]
                if movement in ONE_ARM:
                    joints = mirror_right_arm(joints)
                seqs.append(
                    Sequence(
                        dataset="uiprmd",
                        subject_id=f"uiprmd_s{subject}",
                        exercise=movements[movement],
                        joints=joints,
                        fps=FPS,
                        label=label,
                        rep_labels=[label],
                        meta={"movement": movement, "episode": int(episode)},
                    )
                )
    return seqs

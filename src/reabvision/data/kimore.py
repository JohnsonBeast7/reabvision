"""Loader do KIMORE (spec 01, DAT-04).

Estrutura: <CG|GPP>/<grupo>/<sujeito>/Es<n>/{Raw, Label}
- Raw/JointPosition*.csv: uma linha por quadro, 25 juntas do Kinect v2 × (x, y, z,
  estado de rastreamento 0/1/2), em metros. Há linhas em branco entre os quadros.
- Label/ClinicalAssessment_*.xlsx: pontuações clínicas 0–50 por exercício
  ("clinical TS Ex#n" = pontuação total).

O KIMORE não tem rótulo correto/incorreto: a série é "correta" se a pontuação total
do exercício for ≥ LABEL_THRESHOLD[exercício] (D7). As repetições são segmentadas
automaticamente com o mesmo contador do app (counting/counter.py) e herdam o rótulo.
"""

from __future__ import annotations

import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from reabvision.config import load_exercises
from reabvision.counting.counter import segment_reps
from reabvision.data.sequence import Sequence
from reabvision.features.angles import compute_angles, primary_angle
from reabvision.paths import DATA

RAW = DATA / "raw" / "kimore"
FPS = 30.0
EXERCISES = {"Es1": ("front_raise", 1), "Es5": ("squat", 5)}
# Kinect v2: índices das juntas na ordem do esqueleto comum.
COMMON_INDEX = (4, 8, 5, 9, 6, 10, 12, 16, 13, 17, 14, 18)
# D7: limiar da pontuação total (0–50) por exercício = mediana dos participantes
# saudáveis menos 1 desvio-padrão (critério da spec 01). Calculado com
# kimore_score_summary() em 24/11/2026: agachamento 43,0 − 8,1; elevação 46,3 − 3,9.
LABEL_THRESHOLD = {"squat": 35.0, "front_raise": 42.0}


def read_joint_positions(path: Path) -> np.ndarray:
    """(T, 12, 3) em metros; juntas não rastreadas (estado 0) viram NaN."""
    rows = []
    for line in path.read_text().splitlines():
        parts = [p for p in line.strip().split(",") if p != ""]
        if len(parts) >= 100:
            rows.append([float(p) for p in parts[:100]])
    if not rows:
        return np.empty((0, 12, 3))
    data = np.array(rows).reshape(len(rows), 25, 4)
    xyz = data[:, :, :3].copy()
    xyz[data[:, :, 3] == 0] = np.nan
    return xyz[:, list(COMMON_INDEX)]


def read_score(exercise_dir: Path, number: int) -> float | None:
    files = sorted((exercise_dir / "Label").glob("ClinicalAssessment_*.xlsx"))
    if not files:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        table = pd.read_excel(files[0])
    col = f"clinical TS Ex#{number}"
    if col not in table.columns or table[col].isna().all():
        return None
    return float(table[col].iloc[0])


def _adapt_thresholds(cfg, signal: np.ndarray):
    """Ajusta o limiar de repouso à postura de repouso de cada pessoa.

    No KIMORE vários participantes repousam com o ombro medido em ~40°, acima do
    limiar do app (35°), e o contador nunca via o "repouso". Usa o percentil 10
    (90 no agachamento) do sinal como referência de repouso.
    """
    ok = signal[~np.isnan(signal)]
    if ok.size == 0:
        return cfg
    if cfg.direction == "up":
        rest = max(cfg.rest_threshold, float(np.percentile(ok, 10)) + 10)
        return replace(
            cfg, rest_threshold=rest, active_threshold=max(cfg.active_threshold, rest + 15)
        )
    rest = min(cfg.rest_threshold, float(np.percentile(ok, 90)) - 10)
    return replace(cfg, rest_threshold=rest, active_threshold=min(cfg.active_threshold, rest - 15))


def _group(path: Path) -> tuple[str, str]:
    """(grupo detalhado, saudável|paciente) a partir do caminho."""
    top, group = path.parts[-4], path.parts[-3]  # .../CG/Expert/E_ID1/Es1
    return group, "saudavel" if top == "CG" else "paciente"


def load_kimore(
    raw_dir: Path = RAW, threshold: float | dict[str, float] = LABEL_THRESHOLD
) -> list[Sequence]:
    cfgs = load_exercises()
    seqs = []
    for ex_dir in sorted(raw_dir.glob("*/*/*/Es*")):
        if ex_dir.name not in EXERCISES:
            continue
        exercise, number = EXERCISES[ex_dir.name]
        files = sorted((ex_dir / "Raw").glob("JointPosition*.csv"))
        score = read_score(ex_dir, number)
        if not files or score is None:
            continue
        joints = read_joint_positions(files[0])
        if len(joints) < 30:
            continue
        signal = primary_angle(compute_angles(joints), list(cfgs[exercise].primary_angles))
        cfg = _adapt_thresholds(cfgs[exercise], signal)
        bounds = [(s, e) for s, _, e in segment_reps(signal, FPS, cfg)]
        group, health = _group(ex_dir)
        seqs.append(
            Sequence(
                dataset="kimore",
                subject_id=f"kimore_{ex_dir.parent.name}",
                exercise=exercise,
                joints=joints,
                fps=FPS,
                label=int(
                    score >= (threshold[exercise] if isinstance(threshold, dict) else threshold)
                ),
                meta={
                    "group": group,
                    "health": health,
                    "score": score,
                    "rep_bounds": bounds,
                },
            )
        )
    return seqs


def kimore_score_summary(raw_dir: Path = RAW) -> pd.DataFrame:
    """Pontuações por sujeito/exercício, para escolher o limiar (D7)."""
    rows = []
    for ex_dir in sorted(raw_dir.glob("*/*/*/Es*")):
        if ex_dir.name in EXERCISES:
            exercise, number = EXERCISES[ex_dir.name]
            group, health = _group(ex_dir)
            rows.append(
                {
                    "subject": ex_dir.parent.name,
                    "exercise": exercise,
                    "group": group,
                    "health": health,
                    "score": read_score(ex_dir, number),
                }
            )
    return pd.DataFrame(rows)

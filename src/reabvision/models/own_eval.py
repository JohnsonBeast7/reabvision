"""Cenários C e D: o app inteiro rodando nos vídeos próprios anotados (spec 05).

Para cada vídeo de data/own/annotations.csv roda a mesma ExerciseSession do app
(estimador de pose + contador + regras ou modelo) e mede:
- erro de contagem: |repetições contadas − reais| (META-02: ≤ 1 por série de 10);
- classificação: cada repetição contada é casada com a anotada mais próxima no
  tempo (até MATCH_WINDOW s) e o veredito é comparado com o rótulo anotado.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np

from reabvision.config import load_exercises
from reabvision.models.classifier import load_classifier
from reabvision.paths import DATA
from reabvision.pose import make_estimator
from reabvision.session import ExerciseSession

ANNOTATIONS = DATA / "own" / "annotations.csv"
VIDEOS = DATA / "own" / "videos"
MATCH_WINDOW = 1.0


def read_annotations(path: Path = ANNOTATIONS) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["labels"] = [int(x) for x in r["rep_labels"].split(";") if x != ""]
        r["peaks"] = [float(x) for x in r.get("rep_peaks_s", "").split(";") if x != ""]
    return rows


TARGET_FPS = 30.0


class _Replay:
    """Estimador que devolve poses já calculadas (para rodar vários modelos sem refazer a pose)."""

    def __init__(self, poses: list, name: str):
        self.poses, self.name, self._i = poses, name, 0

    def process(self, frame, timestamp_ms=None):
        pose = self.poses[self._i]
        self._i += 1
        return pose

    def close(self) -> None:
        pass


def estimate_poses(path: Path, estimator: str) -> tuple[list, list[float]]:
    """Poses de cada quadro e seus instantes, reduzindo vídeos de 60 FPS para ~30 FPS."""
    est = make_estimator(estimator)
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or TARGET_FPS
    step = max(1, round(fps / TARGET_FPS))
    poses, times, i = [], [], 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                poses.append(est.process(frame, int(i * 1000 / fps)))
                times.append(i / fps)
            i += 1
    finally:
        cap.release()
        est.close()
    return poses, times


def run_session(poses: list, times: list[float], exercise: str, estimator: str, model: str):
    cfg = load_exercises()[exercise]
    classifier = None if model == "regras" else load_classifier(exercise, model)
    session = ExerciseSession(cfg, _Replay(poses, estimator), classifier)
    dummy = np.zeros((1, 1, 3), np.uint8)
    for t in times:
        session.process(dummy, t)
    session.close()
    return session


def match(pred: list[tuple[float, int]], peaks: list[float], labels: list[int]):
    """Casa (instante, veredito) previstos com as repetições anotadas. Retorna pares (y, ŷ)."""
    pairs, used = [], set()
    for t, verdict in pred:
        dists = [(abs(t - p), k) for k, p in enumerate(peaks) if k not in used]
        if not dists:
            continue
        d, k = min(dists)
        if d <= MATCH_WINDOW:
            used.add(k)
            pairs.append((labels[k], verdict))
    return pairs


def evaluate_own(estimator: str, models: tuple[str, ...] = ("regras", "rf")) -> list[dict]:
    from sklearn.metrics import f1_score

    rows = []
    annotations = [a for a in read_annotations() if (VIDEOS / f"{a['video_id']}.mp4").exists()]
    cache = {
        a["video_id"]: estimate_poses(VIDEOS / f"{a['video_id']}.mp4", estimator)
        for a in annotations
    }
    for model in models:
        per_ex: dict[str, dict] = {}
        for ann in annotations:
            poses, times = cache[ann["video_id"]]
            session = run_session(poses, times, ann["exercise"], estimator, model)
            counted = [r for r in session.reps if r.counted]
            acc = per_ex.setdefault(ann["exercise"], {"errors": [], "pairs": [], "videos": 0})
            acc["videos"] += 1
            acc["errors"].append(abs(len(counted) - int(ann["n_reps_real"])))
            if ann["peaks"] and len(ann["peaks"]) == len(ann["labels"]):
                pred = [(r.peak_t, int(bool(r.correct))) for r in counted]
                acc["pairs"] += match(pred, ann["peaks"], ann["labels"])
        for ex, acc in per_ex.items():
            y = np.array([a for a, _ in acc["pairs"]])
            p = np.array([b for _, b in acc["pairs"]])
            f1 = (
                float(f1_score(y, p, average="macro", zero_division=0))
                if len(y) and len(np.unique(y)) > 1
                else math.nan
            )
            rows.append(
                {
                    "exercicio": ex,
                    "estimador": estimator,
                    "modelo": model,
                    "videos": acc["videos"],
                    "erro_contagem_medio": float(np.mean(acc["errors"])),
                    "erro_contagem_max": int(np.max(acc["errors"])),
                    "reps_casadas": int(len(y)),
                    "acuracia": float((y == p).mean()) if len(y) else math.nan,
                    "f1_macro": f1,
                }
            )
    return rows

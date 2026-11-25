"""Testes de robustez (spec 07, ROB-04 e ROB-06).

    uv run python -m reabvision.robustness.robustness --source rehab24 --videos 4
    uv run python -m reabvision.robustness.robustness --source own

Para cada vídeo e cada condição mede, com MediaPipe e YOLO-pose:
- taxa de detecção: % de quadros com o ângulo principal válido;
- estabilidade: desvio-padrão quadro a quadro do ângulo principal (tremor), em graus;
- erro de contagem: |repetições contadas − reais|;
- FPS do estimador.

Condições:
- "base": vídeo original;
- sintéticas (ROB-06): escuro, baixa resolução, ruído e desfoque, em 3 níveis;
- REHAB24-6: as condições reais vêm dos metadados (luz, pessoa extra, orientação),
  e os vídeos são agrupados por elas no relatório;
- vídeos próprios: `condition_id` de data/own/annotations.csv.
"""

from __future__ import annotations

import argparse
import csv
import tempfile
import time
import zipfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from reabvision.config import load_exercises
from reabvision.paths import DATA, REPORTS
from reabvision.pose import make_estimator

Degrade = Callable[[np.ndarray], np.ndarray]


# --------------------------------------------------------------------- degradações (ROB-06)
def darken(factor: float) -> Degrade:
    return lambda f: np.clip(f.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def low_resolution(width: int) -> Degrade:
    def fn(f: np.ndarray) -> np.ndarray:
        h, w = f.shape[:2]
        small = cv2.resize(f, (width, max(1, round(h * width / w))), interpolation=cv2.INTER_AREA)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)

    return fn


def noise(sigma: float, seed: int = 0) -> Degrade:
    rng = np.random.default_rng(seed)
    return lambda f: np.clip(f + rng.normal(0, sigma, f.shape), 0, 255).astype(np.uint8)


def blur(kernel: int) -> Degrade:
    return lambda f: cv2.GaussianBlur(f, (kernel, kernel), 0)


def far(scale: float) -> Degrade:
    """Simula a pessoa mais longe: reduz a imagem e centraliza numa moldura do tamanho original."""

    def fn(f: np.ndarray) -> np.ndarray:
        h, w = f.shape[:2]
        small = cv2.resize(f, (max(1, int(w * scale)), max(1, int(h * scale))))
        out = np.full_like(f, int(np.median(f)))
        y, x = (h - small.shape[0]) // 2, (w - small.shape[1]) // 2
        out[y : y + small.shape[0], x : x + small.shape[1]] = small
        return out

    return fn


SYNTHETIC: dict[str, Degrade] = {
    "escuro_50": darken(0.5),
    "escuro_25": darken(0.25),
    "escuro_12": darken(0.12),
    "resolucao_320": low_resolution(320),
    "resolucao_160": low_resolution(160),
    "resolucao_96": low_resolution(96),
    "ruido_15": noise(15),
    "ruido_35": noise(35),
    "ruido_60": noise(60),
    "desfoque_7": blur(7),
    "desfoque_15": blur(15),
    "desfoque_31": blur(31),
    "longe_60": far(0.6),
    "longe_40": far(0.4),
    "longe_25": far(0.25),
}


# --------------------------------------------------------------------- vídeos
@dataclass
class VideoItem:
    path: Path
    exercise: str
    true_reps: int | None
    primary: tuple[str, ...]
    meta: dict


def rehab_items(n_per_exercise: int) -> Iterator[VideoItem]:
    """Extrai do zip do REHAB24-6 alguns vídeos de cada exercício (câmera 17)."""
    from reabvision.data.rehab24 import EXERCISE_MAP, ORIENTATION_CAM18, RAW, read_segmentation

    seg = read_segmentation()
    by_ex: dict[str, list[str]] = {}
    for vid, rows in sorted(seg.items()):
        by_ex.setdefault(EXERCISE_MAP[rows[0]["exercise_id"]], []).append(vid)
    tmpdir = Path(tempfile.mkdtemp(prefix="rehab24_"))
    with zipfile.ZipFile(RAW / "videos.zip") as zf:
        names = zf.namelist()
        for exercise, vids in by_ex.items():
            for vid in vids[:n_per_exercise]:
                rows = seg[vid]
                for camera in ("Camera17", "Camera18"):
                    name = next((n for n in names if f"/{vid}-{camera}-" in n), None)
                    if name is None:
                        continue
                    dest = tmpdir / Path(name).name
                    dest.write_bytes(zf.read(name))
                    o17 = rows[0]["cam17_orientation"]
                    extra = (
                        "extra_person_in_cam17" if camera == "Camera17" else "extra_person_in_cam18"
                    )
                    yield VideoItem(
                        path=dest,
                        exercise=exercise,
                        true_reps=len(rows),
                        # Ex1 é com um braço só (o direito).
                        primary=("shoulder_r",)
                        if exercise == "lateral_raise"
                        else ("knee_l", "knee_r"),
                        meta={
                            "video": f"{vid}_{camera}",
                            "orientacao": o17 if camera == "Camera17" else ORIENTATION_CAM18[o17],
                            "luz": "acesa" if rows[0]["lights_on"] == "1" else "apagada",
                            "pessoa_extra": int(rows[0][extra]) >= 2,
                        },
                    )


def own_items(
    annotations: Path = DATA / "own" / "annotations.csv", only: set[str] | None = None
) -> Iterator[VideoItem]:
    cfgs = load_exercises()
    with annotations.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if only and row["video_id"] not in only:
                continue
            path = annotations.parent / "videos" / f"{row['video_id']}.mp4"
            if not path.exists():
                print(f"vídeo ausente: {path}")
                continue
            yield VideoItem(
                path=path,
                exercise=row["exercise"],
                true_reps=int(row["n_reps_real"]) if row.get("n_reps_real") else None,
                primary=cfgs[row["exercise"]].primary_angles,
                meta={"video": row["video_id"], "condicao": row.get("condition_id", "")},
            )


# --------------------------------------------------------------------- métricas
def measure(item: VideoItem, estimator_name: str, degrade: Degrade | None) -> dict:
    """Roda pose (com a degradação) a ~30 FPS e conta com a mesma sessão do app."""
    from dataclasses import replace

    from reabvision.models.own_eval import TARGET_FPS, _Replay
    from reabvision.session import ExerciseSession

    cfg = replace(load_exercises()[item.exercise], primary_angles=tuple(item.primary))
    estimator = make_estimator(estimator_name)
    cap = cv2.VideoCapture(str(item.path))
    fps_video = cap.get(cv2.CAP_PROP_FPS) or TARGET_FPS
    step = max(1, round(fps_video / TARGET_FPS))
    poses, times = [], []
    t0 = time.perf_counter()
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                if degrade is not None:
                    frame = degrade(frame)
                poses.append(estimator.process(frame, int(idx * 1000 / fps_video)))
                times.append(idx / fps_video)
            idx += 1
    finally:
        cap.release()
        estimator.close()
    elapsed = time.perf_counter() - t0

    session = ExerciseSession(cfg, _Replay(poses, estimator_name))
    dummy = np.zeros((1, 1, 3), np.uint8)
    signal = []
    for t in times:
        state = session.process(dummy, t)
        signal.append(np.nan if state.angle is None else state.angle)
    session.close()
    signal = np.array(signal)
    counted = session.counter.count
    diffs = np.abs(np.diff(signal))
    return {
        **item.meta,
        "exercicio": item.exercise,
        "estimador": estimator_name,
        "deteccao": float(np.mean(~np.isnan(signal))) if len(signal) else 0.0,
        "estabilidade": float(np.nanmedian(diffs)) if np.any(~np.isnan(diffs)) else np.nan,
        "reps_reais": item.true_reps,
        "reps_contadas": counted,
        "erro_contagem": abs(counted - item.true_reps) if item.true_reps is not None else np.nan,
        "fps": len(poses) / elapsed if elapsed > 0 else 0.0,
    }


def run(items: list[VideoItem], estimators: list[str], synthetic: bool) -> pd.DataFrame:
    rows = []
    conditions: dict[str, Degrade | None] = {"base": None}
    if synthetic:
        conditions |= SYNTHETIC
    total = len(items) * len(estimators) * len(conditions)
    done = 0
    for item in items:
        for est in estimators:
            for cond, fn in conditions.items():
                done += 1
                r = measure(item, est, fn)
                r["degradacao"] = cond
                rows.append(r)
                print(
                    f"[{done}/{total}] {r['video']} {est} {cond}: detecção {r['deteccao']:.0%} "
                    f"contagem {r['reps_contadas']}/{r['reps_reais']} {r['fps']:.0f} FPS",
                    flush=True,
                )
    return pd.DataFrame(rows)


def write_report(df: pd.DataFrame, name: str) -> Path:
    REPORTS.mkdir(exist_ok=True)
    df.to_csv(REPORTS / f"robustness_{name}.csv", index=False)
    agg = {"deteccao": "mean", "estabilidade": "mean", "erro_contagem": "mean", "fps": "mean"}
    lines = [
        f"# Robustez — {name}",
        "",
        "Gerado por `python -m reabvision.robustness.robustness`.",
        "",
    ]

    def table(group_cols: list[str], title: str) -> None:
        if not all(c in df for c in group_cols):
            return
        g = df.groupby(group_cols).agg(agg).reset_index()
        lines.extend(
            [
                f"## {title}",
                "",
                "| "
                + " | ".join(group_cols)
                + " | detecção | tremor (°/quadro) | erro de contagem | FPS |",
                "|" + "---|" * (len(group_cols) + 4),
            ]
        )
        for _, r in g.iterrows():
            keys = " | ".join(str(r[c]) for c in group_cols)
            lines.append(
                f"| {keys} | {r.deteccao:.0%} | {r.estabilidade:.2f} | "
                f"{r.erro_contagem:.2f} | {r.fps:.0f} |"
            )
        lines.append("")

    table(["degradacao", "estimador"], "Por degradação sintética")
    base = df[df["degradacao"] == "base"]
    for col, title in (
        ("luz", "Luz (REHAB24-6)"),
        ("pessoa_extra", "Pessoa extra na cena"),
        ("orientacao", "Orientação da câmera"),
        ("condicao", "Condição de gravação"),
    ):
        if col in base:
            sub = base
            g = sub.groupby([col, "estimador"]).agg(agg).reset_index()
            lines.extend(
                [
                    f"## {title} (vídeos originais)",
                    "",
                    f"| {col} | estimador | detecção | tremor | erro de contagem | FPS |",
                    "|---|---|---|---|---|---|",
                ]
            )
            for _, r in g.iterrows():
                lines.append(
                    f"| {r[col]} | {r.estimador} | {r.deteccao:.0%} | "
                    f"{r.estabilidade:.2f} | {r.erro_contagem:.2f} | {r.fps:.0f} |"
                )
            lines.append("")
    out = REPORTS / f"robustness_{name}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", choices=["rehab24", "own"], default="rehab24")
    parser.add_argument("--videos", type=int, default=3, help="vídeos por exercício (rehab24)")
    parser.add_argument("--estimators", default="mediapipe,yolo")
    parser.add_argument("--no-synthetic", action="store_true")
    parser.add_argument(
        "--only", default="", help="vídeos próprios a usar (ids separados por vírgula)"
    )
    args = parser.parse_args()
    only = set(filter(None, args.only.split(","))) or None
    items = list(rehab_items(args.videos) if args.source == "rehab24" else own_items(only=only))
    df = run(items, args.estimators.split(","), synthetic=not args.no_synthetic)
    print("ok:", write_report(df, args.source))


if __name__ == "__main__":
    main()

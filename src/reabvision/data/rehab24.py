"""REHAB24-6: extração de pose dos vídeos RGB e carregamento por repetição (spec 01, DAT-10).

Usamos só os exercícios que coincidem com os nossos:
- Ex1 "arm abduction" (um braço, o direito)  -> lateral_raise
- Ex6 "squats"                              -> squat

Cada gravação tem duas câmeras ortogonais (17 e 18). `cam17_orientation` diz se a
pessoa está de frente, meio perfil ou perfil para a câmera 17 (a 18 é o oposto).

    uv run python -m reabvision.data.rehab24 --estimator mediapipe

Os vídeos são lidos de dentro do zip (extraídos um por vez para um arquivo
temporário) e só as coordenadas vão para data/processed/rehab24/<estimador>/.
"""

from __future__ import annotations

import argparse
import csv
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from reabvision.data.sequence import Sequence
from reabvision.paths import DATA

RAW = DATA / "raw" / "rehab24"
PROCESSED = DATA / "processed" / "rehab24"
EXERCISE_MAP = {"1": "lateral_raise", "6": "squat"}
CAMERAS = ("Camera17", "Camera18")
ORIENTATION_CAM18 = {"front": "side", "half-profile": "half-profile", "profile": "front"}


@dataclass
class Rep:
    first: int
    last: int
    correct: int
    lights_on: int
    extra_person: int
    orientation: str


def read_segmentation(path: Path = RAW / "Segmentation.csv") -> dict[str, list[dict]]:
    """video_id -> linhas (uma por repetição) dos exercícios usados."""
    out: dict[str, list[dict]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row["exercise_id"] in EXERCISE_MAP and row["mocap_erroneous"] == "0":
                out.setdefault(row["video_id"], []).append(row)
    return out


def _video_name(zf: zipfile.ZipFile, video_id: str, camera: str) -> str | None:
    for name in zf.namelist():
        if f"/{video_id}-{camera}-" in name and name.endswith(".mp4"):
            return name
    return None


def extract_poses(estimator_name: str = "mediapipe", limit: int | None = None) -> None:
    """Roda o estimador sobre os vídeos usados e salva (T,12,3) + visibilidade em .npz."""
    from reabvision.pose import make_estimator

    seg = read_segmentation()
    out_dir = PROCESSED / estimator_name
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(v, c) for v in sorted(seg) for c in CAMERAS]
    if limit:
        jobs = jobs[:limit]
    with zipfile.ZipFile(RAW / "videos.zip") as zf:
        for i, (video_id, camera) in enumerate(jobs, 1):
            dest = out_dir / f"{video_id}_{camera}.npz"
            if dest.exists():
                continue
            name = _video_name(zf, video_id, camera)
            if name is None:
                print(f"[{i}/{len(jobs)}] sem vídeo: {video_id} {camera}")
                continue
            with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
                tmp.write(zf.read(name))
                tmp.flush()
                joints, vis, fps = _run_video(tmp.name, make_estimator(estimator_name))
            np.savez_compressed(dest, joints=joints, visibility=vis, fps=fps)
            print(f"[{i}/{len(jobs)}] {video_id} {camera}: {len(joints)} quadros", flush=True)


def _run_video(path: str, estimator) -> tuple[np.ndarray, np.ndarray, float]:
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    joints, vis = [], []
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            pose = estimator.process(frame, int(idx * 1000 / fps))
            if pose is None:
                joints.append(np.full((12, 3), np.nan))
                vis.append(np.zeros(12))
            else:
                joints.append(pose.joints)
                vis.append(pose.visibility)
            idx += 1
    finally:
        cap.release()
        estimator.close()
    return np.array(joints), np.array(vis), fps


def load_rehab24(estimator_name: str = "mediapipe") -> list[Sequence]:
    """Uma Sequence por (vídeo, câmera), com as repetições em meta["reps"]."""
    seg = read_segmentation()
    out = []
    for path in sorted((PROCESSED / estimator_name).glob("*.npz")):
        video_id, camera = path.stem.rsplit("_", 1)
        rows = seg.get(video_id)
        if not rows:
            continue
        data = np.load(path)
        o17 = rows[0]["cam17_orientation"]
        orientation = o17 if camera == "Camera17" else ORIENTATION_CAM18[o17]
        extra_key = "extra_person_in_cam17" if camera == "Camera17" else "extra_person_in_cam18"
        reps = [
            Rep(
                first=int(r["first_frame"]),
                last=int(r["last_frame"]),
                correct=int(r["correctness"]),
                lights_on=int(r["lights_on"]),
                extra_person=int(r[extra_key]),
                orientation=orientation,
            )
            for r in rows
        ]
        out.append(
            Sequence(
                dataset="rehab24",
                subject_id=f"rehab24_p{rows[0]['person_id']}",
                exercise=EXERCISE_MAP[rows[0]["exercise_id"]],
                joints=data["joints"],
                fps=float(data["fps"]),
                rep_labels=[r.correct for r in reps],
                meta={
                    "video_id": video_id,
                    "camera": camera,
                    "orientation": orientation,
                    "visibility": data["visibility"],
                    "reps": reps,
                    "subtype": rows[0]["exercise_subtype"],
                },
            )
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai pose dos vídeos do REHAB24-6")
    parser.add_argument("--estimator", default="mediapipe")
    parser.add_argument("--limit", type=int, default=None, help="só os N primeiros vídeos")
    args = parser.parse_args()
    extract_poses(args.estimator, args.limit)


if __name__ == "__main__":
    main()

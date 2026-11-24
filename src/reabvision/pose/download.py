"""Baixa os pesos dos modelos de pose pré-treinados para models/pose/.

Rode antes da apresentação para que o app funcione sem internet:

    uv run python -m reabvision.pose.download
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from reabvision.paths import POSE_MODELS

MEDIAPIPE_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_{variant}/float16/latest/pose_landmarker_{variant}.task"
)
MEDIAPIPE_VARIANTS = ("lite", "full", "heavy")
YOLO_DEFAULT = "yolo11n-pose.pt"


def mediapipe_model_path(variant: str = "full") -> Path:
    if variant not in MEDIAPIPE_VARIANTS:
        raise ValueError(f"variante inválida: {variant}; use uma de {MEDIAPIPE_VARIANTS}")
    path = POSE_MODELS / f"pose_landmarker_{variant}.task"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Baixando modelo MediaPipe '{variant}' para {path} ...")
        urllib.request.urlretrieve(MEDIAPIPE_URL.format(variant=variant), path)
    return path


def yolo_model_path(name: str = YOLO_DEFAULT) -> Path:
    """Caminho local do peso YOLO. O Ultralytics baixa sozinho se não existir."""
    POSE_MODELS.mkdir(parents=True, exist_ok=True)
    return POSE_MODELS / name


def main() -> None:
    for variant in ("lite", "full"):
        print("ok:", mediapipe_model_path(variant))
    from ultralytics import YOLO

    YOLO(str(yolo_model_path()))
    print("ok:", yolo_model_path())


if __name__ == "__main__":
    main()

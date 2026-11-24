"""Estimador MediaPipe BlazePose (Pose Landmarker, API Tasks) — padrão do projeto (D5)."""

from __future__ import annotations

import os
import time

os.environ.setdefault("GLOG_minloglevel", "2")  # silencia avisos internos do MediaPipe

import cv2  # noqa: E402
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

from reabvision.pose.base import PoseResult
from reabvision.pose.download import mediapipe_model_path
from reabvision.skeleton import MEDIAPIPE_INDEX


class MediaPipePose:
    """Usa pose_world_landmarks (metros, centrado no quadril) para os ângulos: 3D (D6)."""

    def __init__(self, variant: str = "full", min_confidence: float = 0.5):
        self.name = f"mediapipe-{variant}"
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(mediapipe_model_path(variant))),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=min_confidence,
            min_pose_presence_confidence=min_confidence,
            min_tracking_confidence=min_confidence,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        self._last_ts = -1

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int | None = None) -> PoseResult | None:
        if timestamp_ms is None:
            timestamp_ms = int(time.monotonic() * 1000)
        # O modo VIDEO exige timestamps estritamente crescentes.
        timestamp_ms = max(int(timestamp_ms), self._last_ts + 1)
        self._last_ts = timestamp_ms

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        if self._landmarker is None:
            raise RuntimeError("estimador já foi fechado")
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.pose_landmarks:
            return None

        h, w = frame_bgr.shape[:2]
        norm = result.pose_landmarks[0]
        world = result.pose_world_landmarks[0]
        image_points = np.array([[lm.x * w, lm.y * h] for lm in norm], dtype=float)
        world_points = np.array([[lm.x, lm.y, lm.z] for lm in world], dtype=float)
        visibility = np.array([lm.visibility or 0.0 for lm in norm], dtype=float)

        idx = list(MEDIAPIPE_INDEX)
        return PoseResult(
            joints=world_points[idx],
            image_points=image_points[idx],
            visibility=visibility[idx],
            is_3d=True,
        )

    def close(self) -> None:
        # Idempotente: fechar duas vezes o landmarker nativo derruba o processo (segfault).
        landmarker, self._landmarker = self._landmarker, None
        if landmarker is not None:
            landmarker.close()

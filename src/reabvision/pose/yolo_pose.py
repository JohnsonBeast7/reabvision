"""Estimador YOLO-pose (Ultralytics) — alternativa ao MediaPipe, sugestão do professor (D5).

Retorna 17 pontos COCO por pessoa; usamos as 12 articulações comuns. Só 2D: os
ângulos são calculados em pixels (coordenadas isotrópicas, sem distorção de
proporção da imagem).

Licença do Ultralytics: AGPL-3.0.
"""

from __future__ import annotations

import numpy as np

from reabvision.pose.base import PoseResult
from reabvision.pose.download import YOLO_DEFAULT, yolo_model_path
from reabvision.skeleton import COCO_INDEX


class YoloPose:
    def __init__(self, weights: str = YOLO_DEFAULT, min_confidence: float = 0.5, imgsz: int = 640):
        from ultralytics import YOLO

        self.name = f"yolo-{weights.removesuffix('.pt')}"
        self._model = YOLO(str(yolo_model_path(weights)))
        self._conf = min_confidence
        self._imgsz = imgsz

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int | None = None) -> PoseResult | None:
        result = self._model.predict(
            frame_bgr, conf=self._conf, imgsz=self._imgsz, device="cpu", verbose=False
        )[0]
        if result.keypoints is None or len(result.boxes) == 0:
            return None

        # Várias pessoas na cena: fica a de maior caixa (a mais próxima da câmera).
        boxes = result.boxes.xyxy.cpu().numpy()
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        person = int(np.argmax(areas))

        kp = result.keypoints.data[person].cpu().numpy()  # (17, 3): x, y, conf
        idx = list(COCO_INDEX)
        xy = kp[idx, :2].astype(float)
        conf = kp[idx, 2].astype(float)
        joints = np.column_stack([xy, np.full(len(idx), np.nan)])
        return PoseResult(joints=joints, image_points=xy, visibility=conf, is_3d=False)

    def close(self) -> None:
        pass

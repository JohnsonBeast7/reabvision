"""Estimadores de pose atrás de uma interface comum."""

from reabvision.pose.base import PoseEstimator, PoseResult

ESTIMATORS = {
    "mediapipe": "MediaPipe BlazePose",
    "mediapipe-lite": "MediaPipe BlazePose (lite, mais rápido)",
    "yolo": "YOLO-pose (Ultralytics)",
}


def make_estimator(name: str = "mediapipe") -> PoseEstimator:
    if name == "mediapipe":
        from reabvision.pose.mediapipe_pose import MediaPipePose

        return MediaPipePose("full")
    if name == "mediapipe-lite":
        from reabvision.pose.mediapipe_pose import MediaPipePose

        return MediaPipePose("lite")
    if name == "yolo":
        from reabvision.pose.yolo_pose import YoloPose

        return YoloPose()
    raise ValueError(f"estimador desconhecido: {name}; use um de {list(ESTIMATORS)}")


__all__ = ["ESTIMATORS", "PoseEstimator", "PoseResult", "make_estimator"]

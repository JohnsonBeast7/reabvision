"""Pipeline completo com um estimador falso (sem câmera nem modelo de pose)."""

import numpy as np

from reabvision.config import load_exercises
from reabvision.pose.base import PoseResult
from reabvision.session import MSG_LOW_VIS, MSG_NO_BODY, ExerciseSession
from reabvision.skeleton import JOINTS, J

FPS = 30.0


def squat_pose(knee_deg: float) -> np.ndarray:
    """Pose 3D (y para cima) com o joelho no ângulo pedido e tronco ereto."""
    p = np.zeros((len(JOINTS), 3))
    rad = np.radians(180 - knee_deg)
    for side, x in (("l", 0.15), ("r", -0.15)):
        ankle = np.array([x, 0.0, 0.0])
        knee = ankle + np.array([0, 0.45, 0])
        hip = knee + 0.45 * np.array([0, np.cos(rad), -np.sin(rad)])
        p[J[f"{side}_ankle"]] = ankle
        p[J[f"{side}_knee"]] = knee
        p[J[f"{side}_hip"]] = hip
        p[J[f"{side}_shoulder"]] = hip + (0, 0.5, 0)
        p[J[f"{side}_elbow"]] = hip + (0, 0.25, 0)
        p[J[f"{side}_wrist"]] = hip + (0, 0.05, 0)
    return p


class FakeEstimator:
    name = "fake"

    def __init__(self, knee_angles, visibility=1.0):
        self.angles = list(knee_angles)
        self.visibility = visibility
        self.i = 0

    def process(self, frame, timestamp_ms=None):
        a = self.angles[self.i]
        self.i += 1
        if a is None:
            return None
        joints = squat_pose(a)
        return PoseResult(
            joints=joints,
            image_points=joints[:, :2] * 100,
            visibility=np.full(len(JOINTS), self.visibility),
            is_3d=True,
        )

    def close(self):
        pass


def knee_series(n_reps, bottom):
    t = np.arange(int(2.5 * FPS)) / (2.5 * FPS)
    one = list(175 - (175 - bottom) * np.sin(np.pi * t)) + [175.0] * int(FPS)
    return [175.0] * int(FPS) + one * n_reps


def run(series, **kw):
    cfg = load_exercises()["squat"]
    session = ExerciseSession(cfg, FakeEstimator(series, **kw), smoothing_alpha=1.0)
    frame = np.zeros((10, 10, 3), np.uint8)
    states = [session.process(frame, i / FPS) for i in range(len(series))]
    return session, states


def test_counts_and_judges_good_reps_by_rules():
    session, _ = run(knee_series(5, bottom=85))
    s = session.summary()
    assert s.total == 5
    assert s.correct == 5
    assert all(r.source == "regras" for r in session.reps)


def test_shallow_reps_get_hint():
    session, _ = run(knee_series(3, bottom=110))  # passa de 120 mas não de 100
    s = session.summary()
    assert s.total == 3
    assert s.incorrect == 3
    assert ("Desça um pouco mais", 3) in s.top_hints


def test_no_body_message():
    _, states = run([None] * 5)
    assert states[-1].message == MSG_NO_BODY
    assert not states[-1].valid


def test_low_visibility_message():
    _, states = run([175.0] * 5, visibility=0.1)
    assert states[-1].message == MSG_LOW_VIS


def test_classifier_is_used_when_given():
    class AlwaysWrong:
        name = "fake-rf"
        threshold = 0.5

        def predict_proba(self, feats, angles):
            return 0.2

    cfg = load_exercises()["squat"]
    series = knee_series(2, bottom=85)
    session = ExerciseSession(cfg, FakeEstimator(series), AlwaysWrong(), smoothing_alpha=1.0)
    frame = np.zeros((10, 10, 3), np.uint8)
    for i in range(len(series)):
        session.process(frame, i / FPS)
    counted = [r for r in session.reps if r.counted]
    assert len(counted) == 2
    assert all(r.correct is False and r.source == "fake-rf" for r in counted)
    assert counted[0].confidence == 0.8


def test_posture_gate_blocks_counting():
    from dataclasses import replace

    from reabvision.session import MSG_POSTURE

    cfg = replace(load_exercises()["squat"], max_trunk_tilt=-1.0)  # todo quadro "curvado"
    series = knee_series(2, bottom=85)
    session = ExerciseSession(cfg, FakeEstimator(series), smoothing_alpha=1.0)
    frame = np.zeros((10, 10, 3), np.uint8)
    states = [session.process(frame, i / FPS) for i in range(len(series))]
    assert session.counter.count == 0
    assert states[-1].message == MSG_POSTURE

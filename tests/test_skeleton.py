import numpy as np
import pytest

from reabvision.skeleton import (
    COCO_INDEX,
    JOINTS,
    KINECT_V2_NAMES,
    MEDIAPIPE_INDEX,
    from_named,
    select,
)


def test_sizes():
    assert len(JOINTS) == len(MEDIAPIPE_INDEX) == len(COCO_INDEX) == len(KINECT_V2_NAMES) == 12


def test_mediapipe_indices_match_landmark_names():
    from mediapipe.tasks.python.vision import PoseLandmark

    expected = {
        "l_shoulder": "LEFT_SHOULDER",
        "r_shoulder": "RIGHT_SHOULDER",
        "l_elbow": "LEFT_ELBOW",
        "r_elbow": "RIGHT_ELBOW",
        "l_wrist": "LEFT_WRIST",
        "r_wrist": "RIGHT_WRIST",
        "l_hip": "LEFT_HIP",
        "r_hip": "RIGHT_HIP",
        "l_knee": "LEFT_KNEE",
        "r_knee": "RIGHT_KNEE",
        "l_ankle": "LEFT_ANKLE",
        "r_ankle": "RIGHT_ANKLE",
    }
    for joint, idx in zip(JOINTS, MEDIAPIPE_INDEX, strict=True):
        assert PoseLandmark(idx).name == expected[joint]


def test_coco_left_right_order():
    # COCO: 5/6 ombros, ..., ímpar = esquerdo (lado do paciente).
    for joint, idx in zip(JOINTS, COCO_INDEX, strict=True):
        assert (idx % 2 == 1) == joint.startswith("l_")


def test_left_right_consistent_across_sources():
    for joint, kinect in zip(JOINTS, KINECT_V2_NAMES, strict=True):
        assert kinect.endswith("Left") == joint.startswith("l_")


def test_select_and_from_named():
    pts = np.arange(33 * 3).reshape(33, 3)
    out = select(pts, MEDIAPIPE_INDEX)
    assert out.shape == (12, 3)
    assert (out[0] == pts[11]).all()
    with pytest.raises(ValueError):
        select(np.zeros((10, 3)), MEDIAPIPE_INDEX)

    named = {n: np.array([i, i, i]) for i, n in enumerate(KINECT_V2_NAMES)}
    assert from_named(named).shape == (12, 3)
    del named["KneeLeft"]
    with pytest.raises(KeyError):
        from_named(named)

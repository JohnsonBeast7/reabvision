import numpy as np
import pytest

from reabvision.features.angles import ANGLE_COLUMNS, angle_between, compute_angles, primary_angle
from reabvision.skeleton import JOINTS, J


def standing_pose() -> np.ndarray:
    """Pessoa em pé, braços ao lado do corpo, y para cima (estilo Kinect)."""
    p = np.zeros((len(JOINTS), 3))
    for side, x in (("l", 0.2), ("r", -0.2)):
        p[J[f"{side}_shoulder"]] = (x, 1.5, 0)
        p[J[f"{side}_elbow"]] = (x, 1.2, 0)
        p[J[f"{side}_wrist"]] = (x, 0.9, 0)
        p[J[f"{side}_hip"]] = (x * 0.5, 1.0, 0)
        p[J[f"{side}_knee"]] = (x * 0.5, 0.5, 0)
        p[J[f"{side}_ankle"]] = (x * 0.5, 0.0, 0)
    return p


@pytest.mark.parametrize("deg", [0, 30, 45, 90, 120, 180])
def test_angle_between_known_values(deg):
    b = np.array([[0.0, 0.0, 0.0]])
    a = np.array([[1.0, 0.0, 0.0]])
    rad = np.radians(deg)
    c = np.array([[np.cos(rad), np.sin(rad), 0.0]])
    assert angle_between(a, b, c)[0] == pytest.approx(deg, abs=1)


def test_standing_pose_is_straight():
    angles = compute_angles(standing_pose()).iloc[0]
    for col in ("knee_l", "knee_r", "elbow_l", "elbow_r"):
        assert angles[col] == pytest.approx(180, abs=1)
    assert angles["trunk_tilt"] == pytest.approx(0, abs=1)
    # Ombro: quadril-ombro-cotovelo com braço caído é ~0-15 graus.
    assert angles["shoulder_l"] < 15


def test_arm_raised_to_shoulder_height_is_90():
    p = standing_pose()
    p[J["l_elbow"]] = (0.5, 1.5, 0)
    p[J["l_wrist"]] = (0.8, 1.5, 0)
    p[J["l_hip"]] = (0.2, 1.0, 0)  # quadril alinhado sob o ombro
    angles = compute_angles(p).iloc[0]
    assert angles["shoulder_l"] == pytest.approx(90, abs=1)
    assert angles["elbow_l"] == pytest.approx(180, abs=1)


def test_knee_at_90_degrees():
    p = standing_pose()
    p[J["l_knee"]] = (0.1, 0.5, 0.5)
    p[J["l_ankle"]] = (0.1, 0.0, 0.5)
    p[J["l_hip"]] = (0.1, 0.5, 0.0)
    assert compute_angles(p).iloc[0]["knee_l"] == pytest.approx(90, abs=1)


def test_2d_input_matches_3d_planar_pose():
    p3 = standing_pose()
    p2 = p3[:, :2]
    a3 = compute_angles(p3)
    a2 = compute_angles(p2)
    np.testing.assert_allclose(a2.to_numpy(), a3.to_numpy(), atol=1e-6)


def test_nan_depth_is_treated_as_2d():
    p = standing_pose()
    p[:, 2] = np.nan
    assert not compute_angles(p).isna().any().any()


def test_trunk_tilt_is_sign_independent():
    p = standing_pose()
    flipped = p.copy()
    flipped[:, 1] *= -1  # y para baixo (imagem)
    assert compute_angles(flipped).iloc[0]["trunk_tilt"] == pytest.approx(0, abs=1)


def test_sequence_shape_and_columns():
    seq = np.stack([standing_pose()] * 5)
    df = compute_angles(seq)
    assert df.shape == (5, len(ANGLE_COLUMNS))
    assert list(df.columns) == list(ANGLE_COLUMNS)


def test_primary_angle_ignores_nan():
    df = compute_angles(standing_pose())
    df.loc[0, "knee_r"] = np.nan
    assert primary_angle(df, ["knee_l", "knee_r"])[0] == pytest.approx(180, abs=1)


def test_rejects_wrong_shape():
    with pytest.raises(ValueError):
        compute_angles(np.zeros((10, 3)))


def test_trunk_tilt_ignores_depth():
    p = standing_pose()
    p[J["l_shoulder"], 2] = 0.5  # ombros "para trás" só na profundidade
    p[J["r_shoulder"], 2] = 0.5
    assert compute_angles(p).iloc[0]["trunk_tilt"] == pytest.approx(0, abs=1)


def test_trunk_tilt_sideways_lean():
    p = standing_pose()
    p[J["l_shoulder"], 0] += 0.5  # tronco inclinado 45° para o lado (ombros 0.5 m acima)
    p[J["r_shoulder"], 0] += 0.5
    assert compute_angles(p).iloc[0]["trunk_tilt"] == pytest.approx(45, abs=1)

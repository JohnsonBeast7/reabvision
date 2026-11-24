import zipfile

import numpy as np
import pytest

from reabvision.data.uiprmd import COMMON_INDEX, PARENT, forward_kinematics, load_uiprmd
from reabvision.features.angles import compute_angles


def offsets() -> np.ndarray:
    """Esqueleto em pé (cm), no formato do UI-PRMD: junta 0 absoluta, demais relativas."""
    o = np.zeros((22, 3))
    o[0] = (0, 100, 200)  # cintura
    o[1], o[2] = (0, 20, 0), (0, 20, 0)  # coluna, peito
    o[3], o[4], o[5] = (0, 5, 0), (0, 10, 0), (0, 10, 0)
    for side, sx in ((6, 1), (10, -1)):  # clavícula, ombro, cotovelo, punho
        o[side] = (sx * 2, 0, 0)
        o[side + 1] = (sx * 15, 0, 0)
        o[side + 2] = (0, -28, 0)
        o[side + 3] = (0, -25, 0)
    for side, sx in ((14, 1), (18, -1)):  # quadril, joelho, tornozelo, dedos
        o[side] = (sx * 10, 0, 0)
        o[side + 1] = (0, -45, 0)
        o[side + 2] = (0, -45, 0)
        o[side + 3] = (0, 0, 12)
    return o


def test_zero_angles_accumulate_offsets():
    pos = offsets()[None]
    glob = forward_kinematics(pos, np.zeros((1, 22, 3)))[0]
    for j, p in enumerate(PARENT):
        expected = pos[0, 0] if p < 0 else glob[p] + pos[0, j]
        np.testing.assert_allclose(glob[j], expected)


def test_knee_rotation_bends_knee():
    pos = offsets()[None]
    ang = np.zeros((1, 22, 3))
    ang[0, 15, 1] = 90  # rotação X no joelho esquerdo
    glob = forward_kinematics(pos, ang)[:, list(COMMON_INDEX)] / 100
    assert compute_angles(glob).iloc[0]["knee_l"] == pytest.approx(90, abs=1)
    assert compute_angles(glob).iloc[0]["knee_r"] == pytest.approx(180, abs=1)


def test_loader_reads_zip_pair(tmp_path):
    row = ",".join(f"{v:.4f}" for v in offsets().ravel())
    zero = ",".join(["0"] * 66)
    for name, folder in (
        ("Segmented Movements.zip", "Segmented Movements"),
        ("Incorrect Segmented Movements.zip", "Incorrect Segmented Movements"),
    ):
        with zipfile.ZipFile(tmp_path / name, "w") as zf:
            for mv in ("m01", "m02"):
                base = f"{folder}/Kinect"
                suffix = "" if folder.startswith("Segmented") else "_inc"
                zf.writestr(
                    f"{base}/Positions/{mv}_s03_e01_positions{suffix}.txt", f"{row}\n{row}\n"
                )
                zf.writestr(f"{base}/Angles/{mv}_s03_e01_angles{suffix}.txt", f"{zero}\n{zero}\n")
    seqs = load_uiprmd(tmp_path)
    assert len(seqs) == 2  # só m01 é usado; uma correta e uma incorreta
    assert {s.label for s in seqs} == {0, 1}
    s = seqs[0]
    assert s.exercise == "squat" and s.subject_id == "uiprmd_s03"
    assert s.joints.shape == (2, 12, 3)
    assert s.joints[0, 0, 1] == pytest.approx(1.4)  # ombro esq. a 1,40 m (cm -> m)

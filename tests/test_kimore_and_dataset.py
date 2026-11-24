import numpy as np
import pandas as pd

from reabvision.data.kimore import load_kimore, read_joint_positions
from reabvision.data.sequence import Sequence
from reabvision.models.dataset import build_repset


def kinect_frame(arm_deg: float) -> list[float]:
    """25 juntas Kinect v2 × (x, y, z, estado). Braços sobem pela frente com arm_deg."""
    j = np.zeros((25, 4))
    j[:, 3] = 2
    rad = np.radians(arm_deg)
    for sh, el, wr, hip, kn, an, x in ((4, 5, 6, 12, 13, 14, -0.2), (8, 9, 10, 16, 17, 18, 0.2)):
        j[sh, :3] = (x, 1.4, 2.0)
        j[el, :3] = (x, 1.4 - 0.3 * np.cos(rad), 2.0 - 0.3 * np.sin(rad))
        j[wr, :3] = (x, 1.4 - 0.55 * np.cos(rad), 2.0 - 0.55 * np.sin(rad))
        j[hip, :3] = (x / 2, 0.9, 2.0)
        j[kn, :3] = (x / 2, 0.5, 2.0)
        j[an, :3] = (x / 2, 0.1, 2.0)
    return j.ravel().tolist()


def write_subject(root, top, group, subject, score):
    ex = root / top / group / subject / "Es1"
    (ex / "Raw").mkdir(parents=True)
    (ex / "Label").mkdir()
    t = np.arange(int(30 * 14)) / 30
    arm = 15 + 140 * (1 - np.cos(2 * np.pi * t / 2.8)) / 2  # 5 elevações de 2,8 s
    lines = []
    for a in arm:
        lines += ["", ",".join(f"{v:.4f}" for v in kinect_frame(a))]
    (ex / "Raw" / "JointPosition1.csv").write_text("\n".join(lines))
    cols = {"Subject ID": [subject]} | {f"clinical TS Ex#{i}": [score] for i in range(1, 6)}
    pd.DataFrame(cols).to_excel(ex / "Label" / f"ClinicalAssessment_{subject}.xlsx", index=False)


def test_read_joint_positions_skips_blank_lines_and_untracked(tmp_path):
    frame = kinect_frame(0)
    frame[4 * 4 + 3] = 0  # ombro esquerdo não rastreado
    path = tmp_path / "j.csv"
    path.write_text("\n\n" + ",".join(map(str, frame)) + "\n\n")
    joints = read_joint_positions(path)
    assert joints.shape == (1, 12, 3)
    assert np.isnan(joints[0, 0]).all() and not np.isnan(joints[0, 1]).any()


def test_load_kimore_labels_and_segments(tmp_path):
    write_subject(tmp_path, "CG", "Expert", "E_ID1", 45.0)
    write_subject(tmp_path, "GPP", "Stroke", "S_ID1", 20.0)
    seqs = {s.subject_id: s for s in load_kimore(tmp_path, threshold=40)}
    assert seqs["kimore_E_ID1"].label == 1 and seqs["kimore_S_ID1"].label == 0
    assert seqs["kimore_S_ID1"].meta["health"] == "paciente"
    assert seqs["kimore_E_ID1"].meta["health"] == "saudavel"
    assert seqs["kimore_E_ID1"].meta["group"] == "Expert"
    assert seqs["kimore_E_ID1"].exercise == "front_raise"
    assert len(seqs["kimore_E_ID1"].meta["rep_bounds"]) == 5

    rs = build_repset(list(seqs.values()))
    assert len(rs) == 10
    assert set(rs.table["label"]) == {0, 1}
    assert rs.sequences.shape[1:] == (64, 9)
    assert "shoulder_l_max" in rs.feature_names


def test_build_repset_single_rep_sequences():
    joints = np.zeros((20, 12, 3))
    joints[:, :, 1] = np.linspace(1.5, 0, 12)  # pose degenerada, mas sem NaN
    seq = Sequence("uiprmd", "uiprmd_s01", "squat", joints, fps=30, label=1)
    rs = build_repset([seq])
    assert len(rs) == 1 and rs.table.loc[0, "label"] == 1

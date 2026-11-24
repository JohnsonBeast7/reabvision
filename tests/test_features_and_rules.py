import math

import numpy as np
import pandas as pd
import pytest

from reabvision.config import EXERCISES, load_exercises
from reabvision.features.angles import ANGLE_COLUMNS
from reabvision.features.repetition import SEQUENCE_LENGTH, rep_features, rep_sequence
from reabvision.feedback import evaluate_rules


def fake_rep(n=60, knee_min=80.0, trunk=10.0) -> pd.DataFrame:
    t = np.linspace(0, np.pi, n)
    knee = 175 - (175 - knee_min) * np.sin(t)
    data = {c: np.full(n, 170.0) for c in ANGLE_COLUMNS}
    data["knee_l"] = knee
    data["knee_r"] = knee + 4
    data["trunk_tilt"] = np.full(n, trunk)
    return pd.DataFrame(data)


def test_rep_features_values():
    f = rep_features(fake_rep(), fps=30)
    assert f["duration"] == pytest.approx(2.0)
    assert f["knee_l_min"] == pytest.approx(80, abs=0.5)
    assert f["knee_l_range"] == pytest.approx(95, abs=0.5)
    assert f["asym_knee"] == pytest.approx(4)
    assert f["knee_l_vel_max"] > 0


def test_rep_features_all_nan_column():
    df = fake_rep()
    df["elbow_l"] = np.nan
    f = rep_features(df, fps=30)
    assert math.isnan(f["elbow_l_min"])


def test_rep_sequence_resamples():
    seq = rep_sequence(fake_rep(n=37))
    assert seq.shape == (SEQUENCE_LENGTH, len(ANGLE_COLUMNS))
    assert not np.isnan(seq).any()


def test_rep_sequence_fills_gaps():
    df = fake_rep()
    df.loc[10:20, "knee_l"] = np.nan
    assert not np.isnan(rep_sequence(df)).any()


def test_config_loads_all_exercises():
    cfgs = load_exercises()
    assert set(cfgs) == set(EXERCISES)


def test_squat_rules():
    cfg = load_exercises()["squat"]
    good = rep_features(fake_rep(knee_min=80, trunk=20), fps=30)
    assert evaluate_rules(cfg, good) == []
    shallow = rep_features(fake_rep(knee_min=130, trunk=20), fps=30)
    assert "Desça um pouco mais" in evaluate_rules(cfg, shallow)
    leaning = rep_features(fake_rep(knee_min=80, trunk=60), fps=30)
    assert "Mantenha o tronco mais ereto" in evaluate_rules(cfg, leaning)


def test_rule_features_must_exist():
    """Todo atributo citado nas regras precisa existir no dicionário de atributos."""
    known = set(rep_features(fake_rep(), fps=30))
    for cfg in load_exercises().values():
        for rule in cfg.rules:
            assert set(rule.features) <= known, (cfg.key, rule.features)

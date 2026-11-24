import numpy as np
import pytest

from reabvision.data.sequence import Sequence, resample


def test_resample_halves_frames():
    x = np.arange(61, dtype=float).reshape(61, 1, 1)  # 2 s a 30 Hz
    y = resample(x, fps_in=30, fps_out=15)
    assert y.shape[0] == 31
    np.testing.assert_allclose(y[:, 0, 0], np.arange(0, 61, 2))


def test_resample_upsamples_and_fills_nan():
    x = np.array([0.0, np.nan, 2.0, 3.0]).reshape(4, 1, 1)
    y = resample(x, fps_in=10, fps_out=20)
    assert y.shape[0] == 7
    assert not np.isnan(y).any()
    assert y[2, 0, 0] == pytest.approx(1.0)


def test_sequence_validates_shape():
    Sequence("own", "own_a", "squat", np.zeros((5, 12, 3)), fps=30)
    with pytest.raises(ValueError):
        Sequence("own", "own_a", "squat", np.zeros((5, 10, 3)), fps=30)

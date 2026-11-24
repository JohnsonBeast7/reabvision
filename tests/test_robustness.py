import numpy as np

from reabvision.robustness.robustness import SYNTHETIC, blur, darken, low_resolution, noise


def test_degradations_keep_shape_and_dtype():
    frame = np.full((48, 64, 3), 200, np.uint8)
    for fn in SYNTHETIC.values():
        out = fn(frame)
        assert out.shape == frame.shape and out.dtype == np.uint8


def test_degradation_effects():
    rng = np.random.default_rng(0)
    frame = rng.integers(0, 256, (48, 64, 3), dtype=np.uint8)
    assert darken(0.5)(frame).mean() < frame.mean() * 0.55
    assert np.abs(noise(30)(frame).astype(int) - frame).mean() > 10
    # baixa resolução e desfoque reduzem o detalhe (variação entre pixels vizinhos)
    detail = lambda f: np.abs(np.diff(f.astype(int), axis=1)).mean()  # noqa: E731
    assert detail(low_resolution(16)(frame)) < detail(frame) / 2
    assert detail(blur(7)(frame)) < detail(frame) / 2

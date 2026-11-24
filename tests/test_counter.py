import numpy as np
import pytest

from reabvision.config import load_exercises
from reabvision.counting.counter import RepCounter, segment_reps, segment_reps_peaks

FPS = 30.0
EXERCISES = load_exercises()


def squat_signal(n_reps=10, period=2.5, rest=175.0, bottom=85.0, pause=1.0, noise=0.0, seed=0):
    """Ângulo do joelho: repouso, desce até `bottom`, sobe, pausa curta."""
    rng = np.random.default_rng(seed)
    one = []
    t = np.arange(int(period * FPS)) / (period * FPS)
    one.extend(rest - (rest - bottom) * np.sin(np.pi * t))
    one.extend([rest] * int(pause * FPS))
    sig = np.array([rest] * int(FPS) + one * n_reps)
    return sig + rng.normal(0, noise, sig.size)


def raise_signal(n_reps=10, top=95.0, rest=15.0, **kw):
    # Espelho do agachamento: ângulo do ombro sobe e desce.
    s = squat_signal(n_reps=n_reps, rest=rest, bottom=top, **kw)
    return s


def run_online(signal, cfg):
    counter = RepCounter(cfg)
    events = [counter.update(v, i / FPS) for i, v in enumerate(signal)]
    return counter, [e for e in events if e is not None]


@pytest.mark.parametrize("noise", [0.0, 3.0])
def test_squat_counts_ten(noise):
    counter, _ = run_online(squat_signal(noise=noise), EXERCISES["squat"])
    assert counter.count == 10


@pytest.mark.parametrize("key", ["lateral_raise", "front_raise"])
def test_raise_counts_ten(key):
    counter, _ = run_online(raise_signal(noise=2.0), EXERCISES[key])
    assert counter.count == 10


def test_partial_rep_not_counted():
    cfg = EXERCISES["squat"]
    full = squat_signal(n_reps=3)
    partial = squat_signal(n_reps=1, bottom=140)  # não chega ao limiar ativo (120)
    counter, events = run_online(np.concatenate([full, partial, full]), cfg)
    assert counter.count == 6
    assert any(e.reason == "incompleta" for e in events)


def test_too_fast_not_counted():
    cfg = EXERCISES["squat"]
    counter, events = run_online(squat_signal(n_reps=3, period=0.4), cfg)
    assert counter.count == 0
    assert all(e.reason == "rapida" for e in events)


def test_short_pose_dropout_keeps_rep():
    sig = squat_signal(n_reps=5)
    # Falha curta (0,2 s) no meio de cada descida.
    for start in range(int(FPS) + 30, sig.size, int(3.5 * FPS)):
        sig[start : start + 6] = np.nan
    counter, _ = run_online(sig, EXERCISES["squat"])
    assert counter.count == 5


def test_long_dropout_discards_rep():
    sig = squat_signal(n_reps=1)
    mid = int(FPS) + int(1.25 * FPS)  # fundo do agachamento
    sig[mid - 30 : mid + 30] = np.nan  # 2 s sem pose
    counter, _ = run_online(sig, EXERCISES["squat"])
    assert counter.count == 0


def test_pause_in_the_middle_of_series():
    sig = np.concatenate([squat_signal(n_reps=4), [175.0] * int(5 * FPS), squat_signal(n_reps=4)])
    counter, _ = run_online(sig, EXERCISES["squat"])
    assert counter.count == 8


@pytest.mark.parametrize("key", ["squat", "lateral_raise"])
def test_offline_methods_agree(key):
    cfg = EXERCISES[key]
    sig = squat_signal(noise=2.0) if key == "squat" else raise_signal(noise=2.0)
    a = segment_reps(sig, FPS, cfg)
    b = segment_reps_peaks(sig, FPS, cfg)
    assert len(a) == len(b) == 10
    for (sa, pa, ea), (sb, pb, eb) in zip(a, b, strict=True):
        assert abs(sa - sb) <= 3 and abs(ea - eb) <= 3
        assert abs(pa - pb) <= 0.3 * FPS


def test_event_amplitude_and_extreme():
    _, events = run_online(squat_signal(n_reps=1), EXERCISES["squat"])
    (event,) = [e for e in events if e.counted]
    assert event.extreme == pytest.approx(85, abs=1)
    assert event.amplitude == pytest.approx(90, abs=2)
    assert event.start_t < event.peak_t < event.end_t

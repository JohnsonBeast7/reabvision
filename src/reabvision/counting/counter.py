"""Contagem de repetições (spec 03).

- RepCounter: versão online, máquina de estados com histerese (REP-01).
- segment_reps: versão offline usando a mesma máquina de estados sobre um sinal inteiro.
- segment_reps_peaks: versão offline com scipy.signal.find_peaks (REP-02), usada para
  conferir a concordância com a máquina de estados.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.signal import find_peaks

from reabvision.config import ExerciseConfig


class State(Enum):
    REST = "repouso"
    MOVING = "movimento"
    ACTIVE = "ativo"


@dataclass(frozen=True)
class RepEvent:
    """Fim de um ciclo de movimento. counted=False quando não valeu como repetição."""

    counted: bool
    start_t: float
    peak_t: float
    end_t: float
    amplitude: float
    extreme: float
    reason: str
    """'ok', 'incompleta', 'rapida' ou 'lenta'."""


class RepCounter:
    def __init__(self, cfg: ExerciseConfig):
        self.cfg = cfg
        self._sign = -1.0 if cfg.direction == "down" else 1.0
        self.reset()

    def reset(self) -> None:
        self.count = 0
        self.state = State.REST
        self._rest_ref: float | None = None
        self._start_t = 0.0
        self._extreme = 0.0
        self._peak_t = 0.0
        self._last_valid_t: float | None = None

    # Convertemos tudo para "quanto maior, mais longe do repouso".
    def _x(self, angle: float) -> float:
        return self._sign * angle

    def update(self, angle: float | None, t: float) -> RepEvent | None:
        """Recebe o ângulo principal do quadro (ou None/NaN se inválido) e o tempo em segundos."""
        cfg = self.cfg
        if angle is None or math.isnan(angle):
            if (
                self.state != State.REST
                and self._last_valid_t is not None
                and t - self._last_valid_t > cfg.max_gap
            ):
                # Falha longa da pose: descarta o ciclo em andamento (pausa a contagem).
                self.state = State.REST
                self._rest_ref = None
            return None
        self._last_valid_t = t

        x = self._x(angle)
        rest = self._x(cfg.rest_threshold)
        active = self._x(cfg.active_threshold)

        if self.state == State.REST:
            if x > rest:
                self.state = State.MOVING
                self._start_t = t
                self._extreme = x
                self._peak_t = t
                if self._rest_ref is None:
                    self._rest_ref = rest
            else:
                # Referência de repouso: o ponto mais "relaxado" visto desde a última rep.
                self._rest_ref = x if self._rest_ref is None else min(self._rest_ref, x)
            return None

        if x > self._extreme:
            self._extreme = x
            self._peak_t = t
        if self.state == State.MOVING and x >= active:
            self.state = State.ACTIVE

        if x > rest:
            return None

        # Voltou ao repouso: fecha o ciclo.
        reached_active = self.state == State.ACTIVE
        duration = t - self._start_t
        amplitude = self._extreme - (self._rest_ref if self._rest_ref is not None else rest)
        if not reached_active or amplitude < cfg.min_amplitude:
            reason = "incompleta"
        elif duration < cfg.min_rep_duration:
            reason = "rapida"
        elif duration > cfg.max_rep_duration:
            reason = "lenta"
        else:
            reason = "ok"
        counted = reason == "ok"
        if counted:
            self.count += 1
        event = RepEvent(
            counted=counted,
            start_t=self._start_t,
            peak_t=self._peak_t,
            end_t=t,
            amplitude=float(amplitude),
            extreme=float(self._sign * self._extreme),
            reason=reason,
        )
        self.state = State.REST
        self._rest_ref = x
        return event


def segment_reps(signal: np.ndarray, fps: float, cfg: ExerciseConfig) -> list[tuple[int, int, int]]:
    """Segmenta o sinal com a máquina de estados. Retorna (início, pico, fim) em quadros."""
    counter = RepCounter(cfg)
    reps = []
    for i, value in enumerate(np.asarray(signal, dtype=float)):
        event = counter.update(value, i / fps)
        if event is not None and event.counted:
            reps.append(
                (
                    round(event.start_t * fps),
                    round(event.peak_t * fps),
                    round(event.end_t * fps),
                )
            )
    return reps


def _fill_nan(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float).copy()
    ok = ~np.isnan(x)
    if ok.sum() == 0:
        return x
    x[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), x[ok])
    return x


def segment_reps_peaks(
    signal: np.ndarray, fps: float, cfg: ExerciseConfig
) -> list[tuple[int, int, int]]:
    """Segmentação offline com find_peaks, usando os mesmos parâmetros do YAML."""
    sign = -1.0 if cfg.direction == "down" else 1.0
    x = sign * _fill_nan(signal)
    rest = sign * cfg.rest_threshold
    active = sign * cfg.active_threshold
    peaks, _ = find_peaks(
        x,
        height=active,
        prominence=cfg.min_amplitude,
        distance=max(1, int(cfg.min_rep_duration * fps / 2)),
    )
    reps: dict[tuple[int, int], tuple[int, int, int]] = {}
    for p in peaks:
        before = np.flatnonzero(x[:p] <= rest)
        after = np.flatnonzero(x[p:] <= rest)
        if before.size == 0 or after.size == 0:
            continue  # ciclo não começa ou não termina em repouso
        start, end = int(before[-1] + 1), int(p + after[0])
        duration = (end - start) / fps
        if not cfg.min_rep_duration <= duration <= cfg.max_rep_duration:
            continue
        key = (start, end)
        # Vários picos dentro do mesmo ciclo: fica o mais alto.
        if key not in reps or x[p] > x[reps[key][1]]:
            reps[key] = (start, int(p), end)
    return sorted(reps.values())

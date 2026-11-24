"""Pipeline de uma série de exercício: quadro -> pose -> ângulos -> contagem -> veredito.

Usado pelo app Streamlit e pela versão em janela OpenCV. Nenhum quadro é guardado:
só as coordenadas/ângulos do quadro atual e da repetição em andamento (ETI-01).
"""

from __future__ import annotations

import math
import time
from collections import Counter, deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from reabvision.config import ExerciseConfig
from reabvision.counting.counter import RepCounter, RepEvent
from reabvision.debug_log import SessionLogger
from reabvision.features.angles import ANGLE_COLUMNS, ANGLE_TRIPLETS, compute_angles, primary_angle
from reabvision.features.repetition import rep_features
from reabvision.feedback import INCOMPLETE_MESSAGES, evaluate_rules
from reabvision.models.classifier import Classifier
from reabvision.pose.base import PoseEstimator, PoseResult
from reabvision.pose.smoothing import JointSmoother
from reabvision.skeleton import J

MSG_NO_BODY = "Corpo não detectado: afaste-se e enquadre o corpo inteiro"
MSG_LOW_VIS = "Articulações pouco visíveis: ajuste a posição da câmera ou a iluminação"


@dataclass
class RepResult:
    index: int
    """Número da repetição contada (0 se não contou)."""
    counted: bool
    correct: bool | None
    confidence: float | None
    source: str
    """'regras', nome do modelo, ou '' quando não houve avaliação."""
    hints: list[str]
    feats: dict[str, float] = field(repr=False, default_factory=dict)


@dataclass
class FrameState:
    pose: PoseResult | None
    valid: bool
    angle: float | None
    count: int
    message: str | None
    new_rep: RepResult | None
    fps: float


@dataclass
class Summary:
    total: int
    correct: int
    incorrect: int
    not_counted: int
    top_hints: list[tuple[str, int]]


class ExerciseSession:
    def __init__(
        self,
        cfg: ExerciseConfig,
        estimator: PoseEstimator,
        classifier: Classifier | None = None,
        smoothing_alpha: float = 0.5,
        min_visibility: float = 0.5,
        logger: SessionLogger | None = None,
    ):
        self.cfg = cfg
        self.estimator = estimator
        self.classifier = classifier
        self.min_visibility = min_visibility
        self.smoother = JointSmoother(smoothing_alpha)
        self.counter = RepCounter(cfg)
        self.reps: list[RepResult] = []
        self._buffer: deque[tuple[float, dict[str, float]]] = deque()
        self._frame_times: deque[float] = deque(maxlen=30)
        self._t0: float | None = None
        self.logger = logger

    # ------------------------------------------------------------------ quadro a quadro
    def process(self, frame_bgr: np.ndarray, t: float | None = None) -> FrameState:
        """Processa um quadro. t em segundos (opcional; padrão: relógio)."""
        now = time.perf_counter()
        if t is None:
            self._t0 = self._t0 if self._t0 is not None else now
            t = now - self._t0
        self._frame_times.append(now)

        pose = self.estimator.process(frame_bgr, int(t * 1000))
        angle = None
        message = None
        row = None
        if pose is None:
            message = MSG_NO_BODY
            self.smoother.reset()
        else:
            row = self._angles_for(pose)
            angle = primary_angle(pd.DataFrame([row]), list(self.cfg.primary_angles))[0]
            if math.isnan(angle):
                angle = None
                message = MSG_LOW_VIS
            else:
                self._buffer.append((t, row))
        self._trim_buffer(t)

        event = self.counter.update(angle, t)
        new_rep = self._close_rep(event) if event is not None else None
        if self.logger is not None:
            self.logger.frame(
                t, angle, self.counter.count, self.counter.state.value, self.fps, message, row
            )
            if event is not None:
                self._log_rep(event, new_rep)

        return FrameState(
            pose=pose,
            valid=angle is not None,
            angle=angle,
            count=self.counter.count,
            message=message,
            new_rep=new_rep,
            fps=self.fps,
        )

    def _angles_for(self, pose: PoseResult) -> dict[str, float]:
        joints = self.smoother(pose.joints)
        row = compute_angles(joints).iloc[0].to_dict()
        # Ângulo com alguma articulação pouco visível vira NaN (ex.: lado oculto na vista lateral).
        for name, triplet in ANGLE_TRIPLETS.items():
            if min(pose.visibility[J[j]] for j in triplet) < self.min_visibility:
                row[name] = math.nan
        trunk = ("l_shoulder", "r_shoulder", "l_hip", "r_hip")
        if max(pose.visibility[J[j]] for j in trunk) < self.min_visibility:
            row["trunk_tilt"] = math.nan
        return row

    def _trim_buffer(self, t: float) -> None:
        # Mantém só o necessário para a repetição mais longa permitida.
        horizon = self.cfg.max_rep_duration + 2.0
        while self._buffer and self._buffer[0][0] < t - horizon:
            self._buffer.popleft()

    # ------------------------------------------------------------------ fim de repetição
    def _close_rep(self, event: RepEvent) -> RepResult:
        rows = [row for (ts, row) in self._buffer if event.start_t <= ts <= event.end_t]
        if not event.counted or len(rows) < 3:
            result = RepResult(
                index=0,
                counted=False,
                correct=None,
                confidence=None,
                source="",
                hints=[INCOMPLETE_MESSAGES.get(event.reason, "Repetição não contada")],
            )
            self.reps.append(result)
            return result

        angles = pd.DataFrame(rows, columns=list(ANGLE_COLUMNS))
        duration = max(event.end_t - event.start_t, 1e-6)
        feats = rep_features(angles, fps=len(rows) / duration)
        hints = evaluate_rules(self.cfg, feats)

        if self.classifier is not None:
            proba = self.classifier.predict_proba(feats, angles)
            correct = proba >= self.classifier.threshold
            confidence = proba if correct else 1 - proba
            source = self.classifier.name
        else:
            correct = not hints
            confidence = None
            source = "regras"

        result = RepResult(
            index=self.counter.count,
            counted=True,
            correct=bool(correct),
            confidence=confidence,
            source=source,
            hints=hints,
            feats=feats,
        )
        self.reps.append(result)
        return result

    def _log_rep(self, event: RepEvent, rep: RepResult) -> None:
        keys = (
            "duration",
            "knee_l_min",
            "knee_r_min",
            "shoulder_l_max",
            "shoulder_r_max",
            "elbow_l_min",
            "elbow_r_min",
            "trunk_tilt_max",
            "asym_knee",
            "asym_shoulder",
        )
        self.logger.rep(
            {
                "start_t": round(event.start_t, 2),
                "end_t": round(event.end_t, 2),
                "reason": event.reason,
                "amplitude": round(event.amplitude, 1),
                "extreme": round(event.extreme, 1),
                "counted": rep.counted,
                "index": rep.index,
                "correct": rep.correct,
                "hints": rep.hints,
                **{k: round(rep.feats[k], 1) for k in keys if k in rep.feats},
            }
        )

    # ------------------------------------------------------------------ resumo
    @property
    def fps(self) -> float:
        if len(self._frame_times) < 2:
            return 0.0
        span = self._frame_times[-1] - self._frame_times[0]
        return (len(self._frame_times) - 1) / span if span > 0 else 0.0

    def summary(self) -> Summary:
        counted = [r for r in self.reps if r.counted]
        hints = Counter(h for r in self.reps for h in r.hints)
        return Summary(
            total=len(counted),
            correct=sum(1 for r in counted if r.correct),
            incorrect=sum(1 for r in counted if r.correct is False),
            not_counted=sum(1 for r in self.reps if not r.counted),
            top_hints=hints.most_common(3),
        )

    def close(self) -> None:
        self.estimator.close()
        if self.logger is not None:
            self.logger.close()

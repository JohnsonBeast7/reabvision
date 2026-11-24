"""Pipeline de uma série de exercício: quadro -> pose -> ângulos -> contagem -> veredito.

Usado pelo app Streamlit e pela versão em janela OpenCV. Nenhum quadro é guardado:
só as coordenadas/ângulos do quadro atual e da repetição em andamento (ETI-01).
"""

from __future__ import annotations

import math
import threading
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
MSG_POSTURE = "Fique em pé, com o tronco reto, para começar"
MSG_BODY_MOVING = "Não contou: mantenha o corpo parado, só os braços se movem"
MSG_TOO_HIGH = "Não contou: eleve só até a altura dos ombros"


def body_height(pose: PoseResult, min_visibility: float = 0.5) -> float:
    """Altura dos ombros na imagem em unidades de "tamanho do tronco".

    Variações grandes dentro de uma repetição indicam que o corpo inteiro subiu ou
    desceu (pulo), e não só os braços. NaN se ombros/quadris pouco visíveis.
    """
    idx = [J[j] for j in ("l_shoulder", "r_shoulder", "l_hip", "r_hip")]
    if min(pose.visibility[i] for i in idx) < min_visibility:
        return math.nan
    pts = pose.image_points
    mid_sh = (pts[J["l_shoulder"]] + pts[J["r_shoulder"]]) / 2
    mid_hip = (pts[J["l_hip"]] + pts[J["r_hip"]]) / 2
    torso = float(np.linalg.norm(mid_sh - mid_hip))
    return float(mid_sh[1] / torso) if torso > 1e-6 else math.nan


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
        # Impede fechar o estimador enquanto um quadro está sendo processado
        # (o Streamlit pode rodar a página de novo em outra thread).
        self._lock = threading.Lock()
        self._closed = False

    # ------------------------------------------------------------------ quadro a quadro
    def process(self, frame_bgr: np.ndarray, t: float | None = None) -> FrameState:
        """Processa um quadro. t em segundos (opcional; padrão: relógio)."""
        with self._lock:
            if self._closed:
                raise RuntimeError("sessão encerrada")
            return self._process(frame_bgr, t)

    def _process(self, frame_bgr: np.ndarray, t: float | None) -> FrameState:
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
            tilt = row.get("trunk_tilt", math.nan)
            if math.isnan(angle):
                angle = None
                message = MSG_LOW_VIS
            elif self.cfg.max_trunk_tilt is not None and tilt > self.cfg.max_trunk_tilt:
                angle = None
                message = MSG_POSTURE
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
        row["body_y"] = body_height(pose, self.min_visibility)
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
            if event.counted:
                self.counter.count -= 1
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

        invalid = self._invalid_reason(event, rows)
        if invalid is not None:
            self.counter.count -= 1  # o contador já tinha contado
            result = RepResult(
                index=0, counted=False, correct=None, confidence=None, source="", hints=[invalid]
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

    def _invalid_reason(self, event: RepEvent, rows: list[dict[str, float]]) -> str | None:
        """Movimentos que passam no contador mas não são o exercício (pulo, polichinelo)."""
        cfg = self.cfg
        if cfg.max_extreme is not None:
            beyond = (
                event.extreme > cfg.max_extreme
                if cfg.direction == "up"
                else (event.extreme < cfg.max_extreme)
            )
            if beyond:
                return MSG_TOO_HIGH
        if cfg.max_body_bounce is not None:
            ys = np.array([r.get("body_y", math.nan) for r in rows], dtype=float)
            ys = ys[~np.isnan(ys)]
            if ys.size >= 3 and ys.max() - ys.min() > cfg.max_body_bounce:
                return MSG_BODY_MOVING
        return None

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
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self.estimator.close()
            if self.logger is not None:
                self.logger.close()

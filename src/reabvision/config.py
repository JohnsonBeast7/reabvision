"""Leitura de configs/exercises.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

from reabvision.features.angles import ANGLE_COLUMNS
from reabvision.paths import CONFIGS

EXERCISES = ("squat", "lateral_raise", "front_raise")


@dataclass(frozen=True)
class Rule:
    features: tuple[str, ...]
    op: Literal[">", "<"]
    value: float
    message: str
    agg: Literal["mean", "min", "max"] = "mean"


@dataclass(frozen=True)
class ExerciseConfig:
    key: str
    name: str
    camera_view: str
    camera: str
    distance: str
    movement: str
    primary_angles: tuple[str, ...]
    direction: Literal["up", "down"]
    rest_threshold: float
    active_threshold: float
    min_amplitude: float
    min_rep_duration: float
    max_rep_duration: float
    max_gap: float
    rules: tuple[Rule, ...] = field(default_factory=tuple)
    max_trunk_tilt: float | None = None
    """Acima desta inclinação do tronco a pessoa não está na postura do exercício
    (ex.: curvada indo até o computador) e o quadro não conta. None = sem limite."""
    max_body_bounce: float | None = None
    """Deslocamento vertical máximo dos ombros na imagem durante a repetição, em
    proporção do tamanho médio do tronco. Acima disso (pulos, deslocamentos) não conta."""
    max_extreme: float | None = None
    """Ângulo principal máximo para a repetição contar (ex.: braços acima da cabeça
    num polichinelo não contam como elevação até a altura dos ombros)."""

    def __post_init__(self):
        if self.direction not in ("up", "down"):
            raise ValueError(f"{self.key}: direction deve ser 'up' ou 'down'")
        if self.direction == "down" and not self.active_threshold < self.rest_threshold:
            raise ValueError(f"{self.key}: com direction=down, active < rest")
        if self.direction == "up" and not self.active_threshold > self.rest_threshold:
            raise ValueError(f"{self.key}: com direction=up, active > rest")
        unknown = set(self.primary_angles) - set(ANGLE_COLUMNS)
        if unknown:
            raise ValueError(f"{self.key}: ângulos desconhecidos {unknown}")


def load_exercises(path: Path | None = None) -> dict[str, ExerciseConfig]:
    path = path or CONFIGS / "exercises.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: dict[str, ExerciseConfig] = {}
    for key, cfg in raw.items():
        rules = tuple(
            Rule(
                features=tuple(r["features"]),
                op=r["op"],
                value=float(r["value"]),
                message=r["message"],
                agg=r.get("agg", "mean"),
            )
            for r in cfg.get("rules", [])
        )
        out[key] = ExerciseConfig(
            key=key,
            name=cfg["name"],
            camera_view=cfg["camera_view"],
            camera=cfg["camera"],
            distance=cfg["distance"],
            movement=cfg["movement"],
            primary_angles=tuple(cfg["primary_angles"]),
            direction=cfg["direction"],
            rest_threshold=float(cfg["rest_threshold"]),
            active_threshold=float(cfg["active_threshold"]),
            min_amplitude=float(cfg["min_amplitude"]),
            min_rep_duration=float(cfg["min_rep_duration"]),
            max_rep_duration=float(cfg["max_rep_duration"]),
            max_gap=float(cfg["max_gap"]),
            rules=rules,
            max_trunk_tilt=cfg.get("max_trunk_tilt"),
            max_body_bounce=cfg.get("max_body_bounce"),
            max_extreme=cfg.get("max_extreme"),
        )
    return out

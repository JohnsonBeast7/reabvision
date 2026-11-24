"""Regras de feedback por exercício (spec 04, MOD-07).

Complementam o classificador com dicas legíveis. Não entram nas métricas.
"""

from __future__ import annotations

import math

import numpy as np

from reabvision.config import ExerciseConfig, Rule

INCOMPLETE_MESSAGES = {
    "incompleta": "Movimento incompleto: complete a amplitude",
    "rapida": "Movimento rápido demais",
    "lenta": "Movimento lento demais ou pausa longa no meio",
}


def _rule_value(rule: Rule, feats: dict[str, float]) -> float:
    values = [feats.get(f, math.nan) for f in rule.features]
    values = [v for v in values if not math.isnan(v)]
    if not values:
        return math.nan
    return float({"mean": np.mean, "min": np.min, "max": np.max}[rule.agg](values))


def evaluate_rules(cfg: ExerciseConfig, feats: dict[str, float]) -> list[str]:
    """Retorna as mensagens das regras violadas, na ordem do YAML."""
    hints = []
    for rule in cfg.rules:
        value = _rule_value(rule, feats)
        if math.isnan(value):
            continue
        violated = value > rule.value if rule.op == ">" else value < rule.value
        if violated:
            hints.append(rule.message)
    return hints

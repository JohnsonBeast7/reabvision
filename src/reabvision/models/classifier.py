"""Interface comum dos classificadores correta × incorreta (spec 04, MOD-05).

O app chama só `predict_proba`, independente do algoritmo. Modelos treinados ficam em
models/<exercício>/<tipo>.joblib (ou .pt para a LSTM).
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import joblib
import numpy as np
import pandas as pd

from reabvision.paths import MODELS

MODEL_KINDS = {"rf": "Random Forest", "lstm": "LSTM"}


class Classifier(Protocol):
    name: str
    threshold: float

    def predict_proba(self, feats: dict[str, float], angles: pd.DataFrame) -> float:
        """Probabilidade de a repetição estar correta (0..1)."""
        ...


class SklearnClassifier:
    """Modelos scikit-learn sobre os atributos por repetição (RF e afins)."""

    def __init__(self, model, feature_names: list[str], threshold: float = 0.5, name: str = "rf"):
        self.model = model
        self.feature_names = list(feature_names)
        self.threshold = threshold
        self.name = name

    def predict_proba(self, feats: dict[str, float], angles: pd.DataFrame | None = None) -> float:
        x = pd.DataFrame(
            [[feats.get(f, np.nan) for f in self.feature_names]], columns=self.feature_names
        )
        return float(self.model.predict_proba(x)[0, 1])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "feature_names": self.feature_names,
                "threshold": self.threshold,
                "name": self.name,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> SklearnClassifier:
        data = joblib.load(path)
        return cls(data["model"], data["feature_names"], data["threshold"], data.get("name", "rf"))


def model_path(exercise: str, kind: str) -> Path:
    suffix = ".pt" if kind == "lstm" else ".joblib"
    return MODELS / exercise / f"{kind}{suffix}"


def available_models(exercise: str) -> list[str]:
    return [k for k in MODEL_KINDS if model_path(exercise, k).exists()]


def load_classifier(exercise: str, kind: str) -> Classifier | None:
    """Carrega o modelo treinado, ou None se ainda não existir."""
    path = model_path(exercise, kind)
    if not path.exists():
        return None
    if kind == "lstm":
        raise NotImplementedError("carregamento da LSTM ainda não implementado (MOD-03)")
    return SklearnClassifier.load(path)

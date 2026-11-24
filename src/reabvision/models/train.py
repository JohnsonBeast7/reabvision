"""Treino dos classificadores correta × incorreta (spec 04, MOD-01).

    uv run python -m reabvision.models.train                      # RF e LSTM, 3 exercícios
    uv run python -m reabvision.models.train --model rf --exercise squat
    uv run python -m reabvision.models.train --train uiprmd,kimore

Validação sempre agrupada por participante (nenhuma pessoa aparece em treino e
validação ao mesmo tempo). O limiar de decisão é escolhido nas predições
fora-da-dobra (validação), nunca no teste (MOD-08). Sementes fixas (MOD-06).
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut

from reabvision.config import EXERCISES
from reabvision.data.sources import load_sources
from reabvision.models.classifier import SklearnClassifier, model_path
from reabvision.models.dataset import RepSet, build_repset
from reabvision.models.lstm import LSTMClassifier, fit_lstm, predict_lstm

SEED = 0
RF_GRID = [
    {"max_depth": None, "min_samples_leaf": 1},
    {"max_depth": None, "min_samples_leaf": 3},
    {"max_depth": 8, "min_samples_leaf": 1},
    {"max_depth": 8, "min_samples_leaf": 3},
]


# --------------------------------------------------------------------- validação
def group_splits(groups: np.ndarray, max_loso: int = 12):
    """Leave-one-subject-out com poucos participantes; GroupKFold(5) com muitos."""
    n = len(np.unique(groups))
    splitter = LeaveOneGroupOut() if n <= max_loso else GroupKFold(n_splits=5)
    return list(splitter.split(np.zeros(len(groups)), groups=groups))


def best_threshold(y: np.ndarray, p: np.ndarray) -> float:
    grid = np.linspace(0.2, 0.8, 25)
    scores = [f1_score(y, p >= t, average="macro", zero_division=0) for t in grid]
    return float(grid[int(np.argmax(scores))])


def metrics(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    pred = (p >= threshold).astype(int)
    return {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "f1_macro": float(f1_score(y, pred, average="macro", zero_division=0)),
        "confusion": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "threshold": threshold,
    }


# --------------------------------------------------------------------- modelos
def make_rf(params: dict) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=SEED, **params
    )


def oof_rf(rs: RepSet, params: dict) -> np.ndarray:
    x = rs.table[rs.feature_names]
    y = rs.table["label"].to_numpy()
    p = np.zeros(len(y))
    for tr, va in group_splits(rs.table["subject_id"].to_numpy()):
        model = make_rf(params).fit(x.iloc[tr], y[tr])
        p[va] = model.predict_proba(x.iloc[va])[:, 1]
    return p


def tune_rf(rs: RepSet) -> tuple[dict, np.ndarray]:
    """Busca pequena de hiperparâmetros por F1 macro na validação agrupada."""
    y = rs.table["label"].to_numpy()
    best = (-1.0, None, None)
    for params in RF_GRID:
        p = oof_rf(rs, params)
        score = f1_score(y, p >= best_threshold(y, p), average="macro", zero_division=0)
        if score > best[0]:
            best = (score, params, p)
    return best[1], best[2]


def oof_lstm(rs: RepSet) -> np.ndarray:
    y = rs.table["label"].to_numpy()
    groups = rs.table["subject_id"].to_numpy()
    p = np.zeros(len(y))
    for tr, va in group_splits(groups):
        tr_in, tr_val = _inner_split(groups[tr])
        net, mean, std = fit_lstm(
            rs.sequences[tr][tr_in], y[tr][tr_in], rs.sequences[tr][tr_val], y[tr][tr_val]
        )
        p[va] = predict_lstm(net, rs.sequences[va], mean, std)
    return p


def _inner_split(groups: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Separa ~20% dos participantes do treino para early stopping."""
    uniq = np.unique(groups)
    rng = np.random.default_rng(SEED)
    val = set(rng.choice(uniq, size=max(1, len(uniq) // 5), replace=False))
    mask = np.array([g in val for g in groups])
    return ~mask, mask


def fit_final(kind: str, rs: RepSet, params: dict | None, threshold: float):
    y = rs.table["label"].to_numpy()
    if kind == "rf":
        model = make_rf(params or {}).fit(rs.table[rs.feature_names], y)
        return SklearnClassifier(model, rs.feature_names, threshold, name="Random Forest")
    groups = rs.table["subject_id"].to_numpy()
    tr, va = _inner_split(groups)
    net, mean, std = fit_lstm(rs.sequences[tr], y[tr], rs.sequences[va], y[va])
    return LSTMClassifier(net, mean, std, threshold, name="LSTM")


TRAINERS: dict[str, Callable[[RepSet], tuple[dict | None, np.ndarray]]] = {
    "rf": tune_rf,
    "lstm": lambda rs: (None, oof_lstm(rs)),
}


def train(exercise: str, kind: str, rs: RepSet, train_sets: list[str]) -> dict:
    rs = rs.subset(rs.table["exercise"] == exercise)
    if len(rs) == 0 or rs.table["label"].nunique() < 2:
        raise ValueError(f"{exercise}: sem dados ou só uma classe")
    t0 = time.time()
    params, oof = TRAINERS[kind](rs)
    y = rs.table["label"].to_numpy()
    threshold = best_threshold(y, oof)
    cv = metrics(y, oof, threshold)
    clf = fit_final(kind, rs, params, threshold)
    path = model_path(exercise, kind)
    clf.save(path)
    info = {
        "exercise": exercise,
        "model": kind,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "train_sets": train_sets,
        "n_reps": int(len(rs)),
        "n_subjects": int(rs.table["subject_id"].nunique()),
        "params": params,
        "cv": cv,
        "seconds": round(time.time() - t0, 1),
    }
    path.with_suffix(".json").write_text(json.dumps(info, indent=2, ensure_ascii=False))
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=["rf", "lstm", "all"], default="all")
    parser.add_argument("--exercise", choices=[*EXERCISES, "all"], default="all")
    parser.add_argument("--train", default="uiprmd,kimore", help="datasets de treino")
    args = parser.parse_args()

    train_sets = args.train.split(",")
    rs = build_repset(load_sources(train_sets))
    exercises = EXERCISES if args.exercise == "all" else (args.exercise,)
    kinds = ("rf", "lstm") if args.model == "all" else (args.model,)
    for ex in exercises:
        for kind in kinds:
            try:
                info = train(ex, kind, rs, train_sets)
            except ValueError as e:
                print(f"pulado: {e}")
                continue
            cv = info["cv"]
            print(
                f"{ex:14s} {kind:4s} n={info['n_reps']:4d} pessoas={info['n_subjects']:3d} "
                f"F1 macro (validação)={cv['f1_macro']:.3f} acc={cv['accuracy']:.3f} "
                f"limiar={cv['threshold']:.2f} ({info['seconds']}s)"
            )


if __name__ == "__main__":
    main()

"""Monta o conjunto de repetições (atributos + sequência + rótulo) a partir das Sequences.

Cada repetição vira uma linha com:
- subject_id, dataset, exercise, label (1 correta / 0 incorreta), meta da condição;
- atributos por repetição (features/repetition.py) para o Random Forest;
- sequência reamostrada (64 × n_ângulos) para a LSTM.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from reabvision.data.sequence import Sequence
from reabvision.features.angles import compute_angles
from reabvision.features.repetition import rep_features, rep_sequence

ID_COLUMNS = ["subject_id", "dataset", "exercise", "label"]


@dataclass
class RepSet:
    table: pd.DataFrame
    """Uma linha por repetição: ID_COLUMNS + meta + atributos."""
    sequences: np.ndarray
    """(N, 64, n_ângulos)."""
    feature_names: list[str] = field(default_factory=list)

    def subset(self, mask) -> RepSet:
        mask = np.asarray(mask, dtype=bool)
        return RepSet(
            self.table[mask].reset_index(drop=True), self.sequences[mask], self.feature_names
        )

    def __len__(self) -> int:
        return len(self.table)


def _rep_windows(seq: Sequence) -> list[tuple[int, int, int, dict]]:
    """(início, fim, rótulo, meta) de cada repetição da Sequence."""
    if "reps" in seq.meta:  # REHAB24-6 / vídeos próprios: janelas anotadas
        return [
            (
                r.first,
                r.last,
                r.correct,
                {k: v for k, v in vars(r).items() if k not in ("first", "last", "correct")},
            )
            for r in seq.meta["reps"]
        ]
    if "rep_bounds" in seq.meta:  # KIMORE: segmentação automática
        return [(a, b, seq.label, {}) for a, b in seq.meta["rep_bounds"]]
    return [(0, len(seq.joints) - 1, seq.label, {})]  # UI-PRMD: arquivo = repetição


def build_repset(seqs: list[Sequence]) -> RepSet:
    rows, sequences = [], []
    for seq in seqs:
        angles_all = compute_angles(seq.joints)
        for start, end, label, extra in _rep_windows(seq):
            if label is None or end - start < 5:
                continue
            angles = angles_all.iloc[start : end + 1].reset_index(drop=True)
            if angles.isna().all().all():
                continue
            feats = rep_features(angles, fps=seq.fps)
            meta = {
                k: v
                for k, v in seq.meta.items()
                if isinstance(v, (str, int, float)) and k not in ("reps",)
            }
            rows.append(
                {
                    "subject_id": seq.subject_id,
                    "dataset": seq.dataset,
                    "exercise": seq.exercise,
                    "label": int(label),
                    **meta,
                    **extra,
                    **feats,
                }
            )
            sequences.append(rep_sequence(angles))
    table = pd.DataFrame(rows)
    feature_names = [c for c in table.columns if c.startswith(_FEATURE_PREFIXES)]
    return RepSet(table, np.array(sequences), feature_names)


_FEATURE_PREFIXES = (
    "duration",
    "knee_",
    "hip_",
    "elbow_",
    "shoulder_",
    "trunk_",
    "asym_",
)

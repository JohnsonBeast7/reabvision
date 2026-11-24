"""Carregamento unificado dos datasets em Sequences."""

from __future__ import annotations

from reabvision.data.sequence import Sequence


def load_sources(names: list[str], estimator: str = "mediapipe") -> list[Sequence]:
    seqs: list[Sequence] = []
    for name in names:
        if name == "uiprmd":
            from reabvision.data.uiprmd import load_uiprmd

            seqs += load_uiprmd()
        elif name == "kimore":
            from reabvision.data.kimore import load_kimore

            seqs += load_kimore()
        elif name == "rehab24":
            from reabvision.data.rehab24 import load_rehab24

            seqs += load_rehab24(estimator)
        else:
            raise ValueError(f"dataset desconhecido: {name}")
    return seqs

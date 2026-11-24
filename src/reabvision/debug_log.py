"""Log numérico de uma sessão, para calibrar limiares (REP-05).

Ativado pela variável de ambiente REABVISION_DEBUG_DIR. Grava só números (ângulos,
estado do contador, repetições e dicas) — nunca imagens (ETI-01).

    REABVISION_DEBUG_DIR=/tmp/log uv run streamlit run src/reabvision/app/main.py

Arquivos por sessão: <dir>/<horário>_<exercício>_frames.csv e ..._reps.jsonl.
"""

from __future__ import annotations

import csv
import json
import math
import os
import time
from pathlib import Path

from reabvision.features.angles import ANGLE_COLUMNS

ENV_VAR = "REABVISION_DEBUG_DIR"


def _num(x: float | None) -> str:
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.2f}"


class SessionLogger:
    def __init__(self, directory: Path, exercise: str, estimator: str):
        directory.mkdir(parents=True, exist_ok=True)
        stem = f"{time.strftime('%Y%m%d_%H%M%S')}_{exercise}_{estimator}"
        self.frames_path = directory / f"{stem}_frames.csv"
        self.reps_path = directory / f"{stem}_reps.jsonl"
        self._frames = self.frames_path.open("w", newline="", encoding="utf-8")
        self._reps = self.reps_path.open("w", encoding="utf-8")
        self._writer = csv.writer(self._frames)
        self._writer.writerow(
            ["t", "valid", "primary", "count", "state", "fps", "message", *ANGLE_COLUMNS]
        )

    def frame(
        self,
        t: float,
        angle: float | None,
        count: int,
        state: str,
        fps: float,
        message: str | None,
        row: dict[str, float] | None,
    ) -> None:
        row = row or {}
        self._writer.writerow(
            [
                f"{t:.3f}",
                int(angle is not None),
                _num(angle),
                count,
                state,
                f"{fps:.1f}",
                message or "",
                *(_num(row.get(c)) for c in ANGLE_COLUMNS),
            ]
        )
        self._frames.flush()

    def rep(self, record: dict) -> None:
        clean = {
            k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in record.items()
        }
        self._reps.write(json.dumps(clean, ensure_ascii=False) + "\n")
        self._reps.flush()

    def close(self) -> None:
        self._frames.close()
        self._reps.close()


def logger_from_env(exercise: str, estimator: str) -> SessionLogger | None:
    directory = os.environ.get(ENV_VAR)
    return SessionLogger(Path(directory), exercise, estimator) if directory else None

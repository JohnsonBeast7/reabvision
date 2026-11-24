"""Caminhos padrão do repositório."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = ROOT / "configs"
MODELS = ROOT / "models"
POSE_MODELS = MODELS / "pose"
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

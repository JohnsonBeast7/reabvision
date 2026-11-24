"""LSTM sobre a sequência de ângulos de cada repetição (spec 04, MOD-03)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from reabvision.features.repetition import rep_sequence


class LSTMNet(nn.Module):
    def __init__(self, n_features: int, hidden: int = 32, layers: int = 1, dropout: float = 0.3):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, num_layers=layers, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, (h, _) = self.lstm(x)
        return self.head(self.drop(h[-1])).squeeze(-1)


def normalize(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """z-score por ângulo; NaN (ângulo ausente) vira 0 = média do treino."""
    z = (x - mean) / std
    return np.nan_to_num(z, nan=0.0)


def fit_lstm(
    x: np.ndarray,
    y: np.ndarray,
    x_val: np.ndarray | None = None,
    y_val: np.ndarray | None = None,
    epochs: int = 80,
    patience: int = 12,
    seed: int = 0,
) -> tuple[LSTMNet, np.ndarray, np.ndarray]:
    """Treina e retorna (rede, média, desvio). Early stopping na validação, se houver."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    mean = np.nanmean(x, axis=(0, 1))
    std = np.nanstd(x, axis=(0, 1)) + 1e-6
    mean, std = np.nan_to_num(mean), np.nan_to_num(std, nan=1.0)
    xt = torch.tensor(normalize(x, mean, std), dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.float32)
    net = LSTMNet(x.shape[2])
    opt = torch.optim.Adam(net.parameters(), lr=3e-3, weight_decay=1e-4)
    pos = max(float(y.sum()), 1.0)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor((len(y) - pos) / pos))

    best, best_state, bad = np.inf, None, 0
    xv = (
        torch.tensor(normalize(x_val, mean, std), dtype=torch.float32)
        if x_val is not None
        else None
    )
    yv = torch.tensor(y_val, dtype=torch.float32) if y_val is not None else None
    gen = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        net.train()
        for idx in torch.randperm(len(xt), generator=gen).split(32):
            opt.zero_grad()
            loss = loss_fn(net(xt[idx]), yt[idx])
            loss.backward()
            opt.step()
        if xv is None:
            continue
        net.eval()
        with torch.no_grad():
            val = loss_fn(net(xv), yv).item()
        if val < best - 1e-4:
            best, bad = val, 0
            best_state = {k: v.clone() for k, v in net.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    if best_state is not None:
        net.load_state_dict(best_state)
    net.eval()
    return net, mean, std


def predict_lstm(net: LSTMNet, x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        logits = net(torch.tensor(normalize(x, mean, std), dtype=torch.float32))
    return torch.sigmoid(logits).numpy()


class LSTMClassifier:
    """Implementa a interface Classifier (models/classifier.py) para o app."""

    def __init__(self, net: LSTMNet, mean, std, threshold: float = 0.5, name: str = "lstm"):
        self.net, self.mean, self.std = net, np.asarray(mean), np.asarray(std)
        self.threshold = threshold
        self.name = name

    def predict_proba(self, feats: dict[str, float], angles: pd.DataFrame) -> float:
        seq = rep_sequence(angles)[None]
        return float(predict_lstm(self.net, seq, self.mean, self.std)[0])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.net.state_dict(),
                "n_features": self.net.lstm.input_size,
                "hidden": self.net.lstm.hidden_size,
                "layers": self.net.lstm.num_layers,
                "mean": self.mean,
                "std": self.std,
                "threshold": self.threshold,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> LSTMClassifier:
        data = torch.load(path, weights_only=False)
        net = LSTMNet(data["n_features"], data["hidden"], data["layers"])
        net.load_state_dict(data["state_dict"])
        net.eval()
        return cls(net, data["mean"], data["std"], data["threshold"])

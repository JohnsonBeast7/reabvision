"""Descoberta das câmeras disponíveis, para o seletor do app.

- Linux: lê os nomes em /sys/class/video4linux. Cada câmera física costuma criar dois
  dispositivos (/dev/videoN para imagem e outro para metadados); fica só o de imagem
  (index == 0).
- Windows/macOS: o OpenCV não informa nomes; testa os índices 0..max_index e lista os
  que abrem como "Câmera N".
"""

from __future__ import annotations

import platform
import re
from pathlib import Path

import cv2

SYSFS = Path("/sys/class/video4linux")


def _linux_cameras(sysfs: Path = SYSFS) -> list[tuple[int, str]]:
    cams = []
    for dev in sorted(sysfs.glob("video*"), key=lambda p: int(re.sub(r"\D", "", p.name) or 0)):
        try:
            if (dev / "index").exists() and (dev / "index").read_text().strip() != "0":
                continue  # nó de metadados da mesma câmera
            name = (dev / "name").read_text().strip()
        except OSError:
            continue
        # Nomes vêm como "Fabricante: Modelo"; o modelo é o mais legível.
        label = name.split(":", 1)[-1].strip() or name
        cams.append((int(re.sub(r"\D", "", dev.name)), label))
    return cams


def _probe_cameras(max_index: int = 4) -> list[tuple[int, str]]:
    cams = []
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        ok = cap.isOpened() and cap.read()[0]
        cap.release()
        if ok:
            cams.append((i, f"Câmera {i}"))
    return cams


def list_cameras() -> list[tuple[int, str]]:
    """Lista (índice para o OpenCV, nome para exibir)."""
    cams = _linux_cameras() if platform.system() == "Linux" and SYSFS.exists() else []
    if not cams:
        cams = _probe_cameras()
    # Nomes repetidos (duas câmeras iguais) ganham o índice para diferenciar.
    labels = [label for _, label in cams]
    return [(i, f"{label} ({i})" if labels.count(label) > 1 else label) for i, label in cams]

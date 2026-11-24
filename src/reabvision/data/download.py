"""Baixa os datasets públicos para data/raw/ (spec 01, DAT-01).

    uv run python -m reabvision.data.download            # todos
    uv run python -m reabvision.data.download uiprmd     # só um

Fontes (ver specs/01-dados.md):
- UI-PRMD: site oficial fora do ar; arquivos originais no Internet Archive. CC BY 4.0.
- REHAB24-6: Zenodo 10.5281/zenodo.13305826. CC BY-NC 4.0.
- KIMORE: site oficial fora do ar; cópia dos arquivos originais no Google Drive.
  Baixa só Es1/Es5, posições das articulações, timestamps e rótulos clínicos.

Os downloads são retomáveis: arquivos já completos são pulados.
"""

from __future__ import annotations

import csv
import hashlib
import html
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

from reabvision.paths import DATA

RAW = DATA / "raw"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0"

UIPRMD_BASE = "http://web.archive.org/web/2025id_/https://webpages.uidaho.edu/ui-prmd/"
UIPRMD_FILES = {
    "Segmented Movements.zip": 206_962_745,
    "Incorrect Segmented Movements.zip": 213_516_724,
}

REHAB_RECORD = "https://zenodo.org/records/13305826"
REHAB_FILES = {
    "Segmentation.csv": None,
    "Segmentation.txt": None,
    "joints_names.txt": None,
    "videos.zip": "ed183a245a1b171638e422f7a288e5a8",
}

KIMORE_DRIVE_ROOT = "1b1anGzSytePiCUyoz8AlGMV2G54e_ZeC"
KIMORE_EXERCISES = {"Es1", "Es5"}


def _request(url: str, referer: str | None = None) -> urllib.request.Request:
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    return urllib.request.Request(url, headers=headers)


def _fetch(url: str, dest: Path, referer: str | None = None, retries: int = 4) -> None:
    """Baixa para dest via arquivo .part (retomável com Range)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(retries):
        try:
            req = _request(url, referer)
            done = part.stat().st_size if part.exists() else 0
            if done:
                req.add_header("Range", f"bytes={done}-")
            with urllib.request.urlopen(req, timeout=60) as resp:
                mode = "ab" if done and resp.status == 206 else "wb"
                with part.open(mode) as f:
                    shutil.copyfileobj(resp, f, length=1 << 20)
            part.rename(dest)
            return
        except Exception as e:  # rede instável: tenta de novo
            if attempt == retries - 1:
                raise RuntimeError(f"falha ao baixar {url}: {e}") from e
            time.sleep(3 * (attempt + 1))


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_uiprmd() -> None:
    out = RAW / "uiprmd"
    for name, size in UIPRMD_FILES.items():
        dest = out / name
        if dest.exists() and dest.stat().st_size == size:
            print(f"ok (já existe): {dest}")
            continue
        print(f"baixando UI-PRMD {name} ...", flush=True)
        _fetch(UIPRMD_BASE + name.replace(" ", "%20"), dest)
        if dest.stat().st_size != size:
            raise RuntimeError(f"{dest}: tamanho inesperado")
        print(f"ok: {dest}")


def download_rehab24() -> None:
    out = RAW / "rehab24"
    for name, md5 in REHAB_FILES.items():
        dest = out / name
        if dest.exists() and (md5 is None or _md5(dest) == md5):
            print(f"ok (já existe): {dest}")
            continue
        print(f"baixando REHAB24-6 {name} ...", flush=True)
        _fetch(f"{REHAB_RECORD}/files/{name}?download=1", dest, referer=REHAB_RECORD)
        if md5 and _md5(dest) != md5:
            raise RuntimeError(f"{dest}: MD5 não confere")
        print(f"ok: {dest}")


def _drive_ls(folder_id: str) -> list[tuple[str, str, bool]]:
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(_request(url), timeout=60).read()
            text = raw.decode("utf-8", "ignore")
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    entries = []
    pattern = (
        r'<div class="flip-entry" id="entry-([^"]+)".*?'
        r'<div class="flip-entry-title">(.*?)</div>'
    )
    for m in re.finditer(pattern, text, re.S):
        is_folder = "/drive/folders/" in text[m.start() : m.end() + 600]
        entries.append((m.group(1), html.unescape(m.group(2)), is_folder))
    return entries


def download_kimore() -> None:
    out = RAW / "kimore"
    manifest: list[tuple[str, str]] = []

    def walk(folder_id: str, rel: Path) -> None:
        for entry_id, name, is_folder in _drive_ls(folder_id):
            path = rel / name
            if is_folder:
                # Estrutura: CG|GPP / grupo / sujeito / EsN / {Raw, Label, Script}
                if len(path.parts) == 4 and name not in KIMORE_EXERCISES:
                    continue
                if name == "Script":
                    continue
                walk(entry_id, path)
                continue
            if name.lower().endswith((".avi", ".mp4")) or name.startswith("JointOrientation"):
                continue
            dest = out / path
            if not dest.exists() or dest.stat().st_size == 0:
                url = f"https://drive.google.com/uc?export=download&id={entry_id}"
                _fetch(url, dest)
                if dest.read_bytes()[:15].lower().startswith(b"<!doctype html"):
                    dest.unlink()
                    print(f"FALHA (Drive devolveu HTML): {path}", flush=True)
                    continue
                time.sleep(0.2)
            manifest.append((str(path), entry_id))
            print(f"ok: {path}", flush=True)

    walk(KIMORE_DRIVE_ROOT, Path())
    with (out / "manifest_drive.csv").open("w", newline="") as f:
        csv.writer(f).writerows([("arquivo", "drive_id"), *manifest])
    print(f"KIMORE: {len(manifest)} arquivos")


DATASETS = {"uiprmd": download_uiprmd, "rehab24": download_rehab24, "kimore": download_kimore}


def main(argv: list[str] | None = None) -> None:
    names = (argv if argv is not None else sys.argv[1:]) or list(DATASETS)
    unknown = set(names) - set(DATASETS)
    if unknown:
        raise SystemExit(f"datasets desconhecidos: {sorted(unknown)}; use {list(DATASETS)}")
    for name in names:
        DATASETS[name]()


if __name__ == "__main__":
    main()

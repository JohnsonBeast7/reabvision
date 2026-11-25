"""Avaliação dos cenários da spec 05 e geração de reports/results.md (AVA-02).

    uv run python -m reabvision.models.evaluate

Cenários (sempre com pessoas de teste fora do treino):
- A: UI-PRMD -> UI-PRMD (leave-one-subject-out)
- B: UI-PRMD + KIMORE (80% das pessoas) -> KIMORE (20%), separado saudáveis × pacientes
- C/D: UI-PRMD + KIMORE -> vídeos próprios (MediaPipe / YOLO) — quando existirem
- F: UI-PRMD + KIMORE -> REHAB24-6 (agachamento e elevação lateral), por condição

As métricas usam limiar 0,5 (os modelos usam class_weight balanceado), para não
escolher o limiar olhando o teste.
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from reabvision.config import EXERCISES
from reabvision.data.sources import load_sources
from reabvision.models.dataset import RepSet, build_repset
from reabvision.models.lstm import fit_lstm, predict_lstm
from reabvision.models.train import (
    SEED,
    _inner_split,
    group_splits,
    make_rf,
    metrics,
)
from reabvision.paths import REPORTS

THRESHOLD = 0.5
RF_PARAMS = {"max_depth": None, "min_samples_leaf": 1}


def _fit_predict(kind: str, train: RepSet, test: RepSet) -> np.ndarray:
    y = train.table["label"].to_numpy()
    if kind == "rf":
        model = make_rf(RF_PARAMS).fit(train.table[train.feature_names], y)
        return model.predict_proba(test.table[train.feature_names])[:, 1]
    tr, va = _inner_split(train.table["subject_id"].to_numpy())
    net, mean, std = fit_lstm(train.sequences[tr], y[tr], train.sequences[va], y[va])
    return predict_lstm(net, test.sequences, mean, std)


def _align(test: RepSet, train: RepSet) -> RepSet:
    """Garante as mesmas colunas de atributos (NaN onde faltar)."""
    table = test.table.copy()
    for col in train.feature_names:
        if col not in table:
            table[col] = np.nan
    return RepSet(table, test.sequences, train.feature_names)


def scenario_a(uiprmd: RepSet) -> list[dict]:
    rows = []
    for ex in EXERCISES:
        rs = uiprmd.subset(uiprmd.table["exercise"] == ex)
        y = rs.table["label"].to_numpy()
        for kind in ("rf", "lstm"):
            p = np.zeros(len(y))
            for tr, va in group_splits(rs.table["subject_id"].to_numpy()):
                p[va] = _fit_predict(
                    kind,
                    rs.subset(np.isin(range(len(y)), tr)),
                    rs.subset(np.isin(range(len(y)), va)),
                )
            rows.append(
                {
                    "cenario": "A",
                    "exercicio": ex,
                    "modelo": kind,
                    "grupo": "todos",
                    **metrics(y, p, THRESHOLD),
                }
            )
    return rows


def scenario_b(uiprmd: RepSet, kimore: RepSet) -> list[dict]:
    rows = []
    subjects = kimore.table.drop_duplicates("subject_id")[["subject_id", "health"]]
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    _, te_idx = next(gss.split(subjects, groups=subjects["subject_id"]))
    test_subjects = set(subjects.iloc[te_idx]["subject_id"])
    is_test = kimore.table["subject_id"].isin(test_subjects).to_numpy()
    for ex in ("squat", "front_raise"):
        train = _concat(
            uiprmd.subset(uiprmd.table["exercise"] == ex),
            kimore.subset(~is_test & (kimore.table["exercise"] == ex).to_numpy()),
        )
        test = _align(kimore.subset(is_test & (kimore.table["exercise"] == ex).to_numpy()), train)
        if len(test) == 0 or test.table["label"].nunique() < 2:
            continue
        for kind in ("rf", "lstm"):
            p = _fit_predict(kind, train, test)
            y = test.table["label"].to_numpy()
            rows.append(
                {
                    "cenario": "B",
                    "exercicio": ex,
                    "modelo": kind,
                    "grupo": "todos",
                    **metrics(y, p, THRESHOLD),
                }
            )
            for health in ("saudavel", "paciente"):
                m = (test.table["health"] == health).to_numpy()
                if m.sum() and len(np.unique(y[m])) > 1:
                    rows.append(
                        {
                            "cenario": "B",
                            "exercicio": ex,
                            "modelo": kind,
                            "grupo": health,
                            **metrics(y[m], p[m], THRESHOLD),
                        }
                    )
    return rows


def scenario_external(
    name: str, train_all: RepSet, test_all: RepSet, condition_cols: tuple[str, ...] = ()
) -> list[dict]:
    rows = []
    for ex in EXERCISES:
        test = test_all.subset(test_all.table["exercise"] == ex)
        if len(test) == 0:
            continue
        train = train_all.subset(train_all.table["exercise"] == ex)
        test = _align(test, train)
        y = test.table["label"].to_numpy()
        for kind in ("rf", "lstm"):
            p = _fit_predict(kind, train, test)
            rows.append(
                {
                    "cenario": name,
                    "exercicio": ex,
                    "modelo": kind,
                    "grupo": "todos",
                    **metrics(y, p, THRESHOLD),
                }
            )
            for col in condition_cols:
                if col not in test.table:
                    continue
                for value, idx in test.table.groupby(col).groups.items():
                    m = np.isin(np.arange(len(y)), list(idx))
                    if m.sum() >= 10 and len(np.unique(y[m])) > 1:
                        rows.append(
                            {
                                "cenario": name,
                                "exercicio": ex,
                                "modelo": kind,
                                "grupo": f"{col}={value}",
                                **metrics(y[m], p[m], THRESHOLD),
                            }
                        )
    return rows


def scenario_mixed(name: str, base: RepSet, target: RepSet) -> list[dict]:
    """Treina com base + target menos uma pessoa do target; testa nessa pessoa."""
    rows = []
    for ex in EXERCISES:
        tgt = target.subset(target.table["exercise"] == ex)
        if len(tgt) == 0:
            continue
        src = base.subset(base.table["exercise"] == ex)
        y = tgt.table["label"].to_numpy()
        for kind in ("rf", "lstm"):
            p = np.zeros(len(y))
            for subj in tgt.table["subject_id"].unique():
                m = (tgt.table["subject_id"] == subj).to_numpy()
                train = _concat(src, tgt.subset(~m))
                p[m] = _fit_predict(kind, train, _align(tgt.subset(m), train))
            rows.append(
                {
                    "cenario": name,
                    "exercicio": ex,
                    "modelo": kind,
                    "grupo": "todos",
                    **metrics(y, p, THRESHOLD),
                }
            )
    return rows


def _concat(a: RepSet, b: RepSet) -> RepSet:
    table = pd.concat([a.table, b.table], ignore_index=True)
    feats = [c for c in a.feature_names if c in b.feature_names] or a.feature_names
    return RepSet(table, np.concatenate([a.sequences, b.sequences]), feats)


def write_report(rows: list[dict], pending: list[str], own: list[dict] | None = None) -> None:
    REPORTS.mkdir(exist_ok=True)
    df = pd.DataFrame(rows)
    (REPORTS / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    lines = [
        "# Resultados da avaliação",
        "",
        f"Gerado automaticamente por `python -m reabvision.models.evaluate` em "
        f"{time.strftime('%Y-%m-%d %H:%M')}. Limiar de decisão fixo em {THRESHOLD}.",
        "Pessoas de teste nunca aparecem no treino. Meta: F1 macro ≥ 0,80.",
        "",
    ]
    titles = {
        "A": "Cenário A — UI-PRMD, deixando uma pessoa de fora",
        "B": "Cenário B — KIMORE (pessoas não vistas), saudáveis × pacientes",
        "F": "Cenário F — treino só com Kinect, teste no REHAB24-6 (vídeo RGB): diferença "
        "Kinect × webcam",
        "F2": "Cenário F2 — treino com Kinect + REHAB24-6, testando cada pessoa do REHAB24-6 "
        "fora do treino",
    }
    for code, title in titles.items():
        part = df[df["cenario"] == code] if len(df) else df
        lines += [f"## {title}", ""]
        if part.empty:
            lines += [
                "_Pendente: " + next((p for p in pending if p.startswith(code)), "sem dados") + "_",
                "",
            ]
            continue
        lines += [
            "| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |",
            "|---|---|---|---|---|---|",
        ]
        for _, r in part.iterrows():
            lines.append(
                f"| {r.exercicio} | {r.grupo} | {r.modelo.upper()} | {r.n} | "
                f"{r.f1_macro:.3f} | {r.accuracy:.3f} |"
            )
        lines.append("")
    lines += [
        "## Cenários C e D — app completo nos vídeos próprios (C: MediaPipe, D: YOLO-pose)",
        "",
    ]
    if not own:
        lines += ["_Pendente: vídeos próprios ainda não anotados_", ""]
    else:
        lines += [
            "Rótulos dos vídeos anotados por inspeção visual; erro de contagem por vídeo "
            "(meta ≤ 1 por série de 10).",
            "",
            "| Exercício | Estimador | Avaliação | Vídeos | Erro de contagem (média / máx) "
            "| Reps casadas | Acurácia | F1 macro |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in own:
            f1 = "—" if r["f1_macro"] != r["f1_macro"] else f"{r['f1_macro']:.3f}"
            lines.append(
                f"| {r['exercicio']} | {r['estimador']} | {r['modelo']} | {r['videos']} | "
                f"{r['erro_contagem_medio']:.2f} / {r['erro_contagem_max']} | "
                f"{r['reps_casadas']} | {r['acuracia']:.3f} | {f1} |"
            )
        lines.append("")
    (REPORTS / "results.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, pending = [], []
    uiprmd = build_repset(load_sources(["uiprmd"]))
    print("cenário A ...", flush=True)
    rows += scenario_a(uiprmd)
    try:
        kimore = build_repset(load_sources(["kimore"]))
        print("cenário B ...", flush=True)
        rows += scenario_b(uiprmd, kimore)
        train_all = _concat(uiprmd, kimore)
    except FileNotFoundError:
        pending.append("B: KIMORE não baixado")
        train_all = uiprmd
    try:
        rehab = build_repset(load_sources(["rehab24"]))
        if len(rehab):
            print("cenário F ...", flush=True)
            rows += scenario_external(
                "F", train_all, rehab, ("orientation", "lights_on", "extra_person")
            )
            print("cenário F2 ...", flush=True)
            rows += scenario_mixed("F2", train_all, rehab)
        else:
            pending.append("F: poses do REHAB24-6 ainda não extraídas")
    except FileNotFoundError:
        pending.append("F: REHAB24-6 não baixado")
    from reabvision.models.own_eval import evaluate_own

    print("cenários C e D ...", flush=True)
    own = evaluate_own("mediapipe") + evaluate_own("yolo")
    write_report(rows, pending, own)
    print(f"ok: {REPORTS / 'results.md'}")


if __name__ == "__main__":
    main()

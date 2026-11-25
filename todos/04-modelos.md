# 04 — Modelos

Spec: [04-modelos.md](../specs/04-modelos.md)

## Base comum

- [x] Interface `Classifier.predict_proba(rep) -> float` (MOD-05)
- [x] Script `train.py --model <rf|lstm> --exercise <...>` salvando modelo + metadados em `models/<exercise>/` (MOD-01)
- [x] Sementes fixas e treino reprodutível (MOD-06)
- [x] Escolha do limiar de decisão na validação, nunca no teste (MOD-08)

## Random Forest

- [x] RF com `class_weight="balanced"` por exercício (MOD-02)
- [x] Busca de hiperparâmetros com `GroupKFold` por participante (MOD-02)
- [ ] Exportar importância dos atributos

## LSTM

- [x] Dataset/DataLoader PyTorch com sequências por repetição (MOD-03)
- [x] LSTM pequena (1–2 camadas, 32–64 unidades, dropout) (MOD-03)
- [x] Early stopping com validação agrupada por participante (MOD-03)
- [ ] Notebook para treinar no Colab, se a CPU local for lenta

## Alternativa leve (PODE)

- [ ] 1D-CNN pequena sobre as mesmas sequências **(PODE)** (MOD-04)
- [ ] GRU **(PODE)** (MOD-04)
- [ ] `HistGradientBoostingClassifier` sobre os atributos do RF **(PODE)** (MOD-04)

## Feedback e inferência

- [x] Regras de feedback por exercício com limiares em `configs/exercises.yaml` (MOD-07)
- [ ] Medir tempo de inferência por repetição (< 50 ms em CPU) (MOD-09)
- [x] Treinar e salvar modelos finais dos 3 exercícios
- [x] Escolher modelo do app pelo F1 macro (empate < 0,02 → RF) e registrar justificativa (D4) — app usa as regras; RF/LSTM falharam em câmera comum

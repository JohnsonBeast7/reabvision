# 04 — Modelos de classificação

Tarefa: dada **uma repetição**, classificar como correta (1) ou incorreta (0). Um modelo por exercício (3 modelos por algoritmo) — mais simples e os erros típicos de cada exercício são diferentes. Treinar um modelo único com o exercício como atributo PODE ser testado.

O professor questionou se a LSTM é o melhor modelo e sugeriu testar. Por isso a spec trata a escolha do modelo como **experimento**, não como premissa.

## Modelos

### M1 — Random Forest (baseline e padrão do app)

- `sklearn.ensemble.RandomForestClassifier`, entrada = atributos por repetição ([02](02-pose-e-features.md#atributos-por-repetição-entrada-do-random-forest)).
- `class_weight="balanced"`.
- Busca de hiperparâmetros pequena (`n_estimators`, `max_depth`, `min_samples_leaf`) com validação cruzada **agrupada por participante** (`GroupKFold`).
- Saída extra: importância dos atributos (ajuda a explicar o feedback e entra no relatório).

### M2 — LSTM

- PyTorch. Entrada = sequência `(64, n_ângulos)` por repetição.
- Arquitetura pequena (dados são poucos): 1–2 camadas, 32–64 unidades, dropout, camada linear + sigmoide.
- Early stopping em validação agrupada por participante.
- Treino cabe em CPU ou Colab gratuito.

### M3 — Alternativa leve (PODE, recomendado)

Para responder de verdade "LSTM é o melhor?", comparar com pelo menos uma destas:

- **1D-CNN** pequena sobre a mesma sequência (costuma igualar LSTM com menos dados e é mais rápida);
- **GRU** (variante mais simples da LSTM);
- **Gradient boosting** (`HistGradientBoostingClassifier`) sobre os mesmos atributos do RF.

### Regras de feedback (complemento, não é modelo treinado)

Além do veredito do classificador, regras simples por exercício geram dicas legíveis, por exemplo:

- agachamento: amplitude do joelho insuficiente → "Desça um pouco mais"; inclinação de tronco alta → "Mantenha o tronco mais ereto";
- elevações de braço: assimetria entre braços alta → "Eleve os dois braços igualmente"; ângulo do ombro baixo → "Eleve mais o braço".

Limiares em `configs/exercises.yaml`. As regras não entram nas métricas de classificação.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| MOD-01 | Script `train.py --model rf --exercise squat` que treina e salva o modelo em `models/<exercise>/<model>.joblib\|.pt` com metadados (data, hash dos dados, hiperparâmetros, métricas de validação) | DEVE |
| MOD-02 | Random Forest por exercício | DEVE |
| MOD-03 | LSTM por exercício | DEVE |
| MOD-04 | Pelo menos uma alternativa M3 | PODE |
| MOD-05 | Interface comum `Classifier.predict_proba(rep) -> float` usada pelo app, independente do algoritmo | DEVE |
| MOD-06 | Sementes fixas; treino reprodutível | DEVE |
| MOD-07 | Regras de feedback por exercício | DEVE |
| MOD-08 | Limiar de decisão escolhido na validação (não no teste) | DEVE |
| MOD-09 | Inferência de uma repetição < 50 ms em CPU | DEVE |

## Escolha do modelo para o app

O app usa o modelo com maior F1 macro no teste por participante; em empate técnico (diferença < 0,02), fica o RF por ser mais rápido e explicável (D4). A escolha e a justificativa vão para o relatório.

## Critérios de aceite

- Modelos RF e LSTM treinados para os 3 exercícios, salvos e carregáveis pelo app.
- Tabela comparativa gerada pelo script de avaliação ([05](05-avaliacao.md)).

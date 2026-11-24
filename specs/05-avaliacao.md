# 05 — Avaliação

## Princípio: divisão por participante

Pessoas do teste **nunca** aparecem no treino nem na validação. Evita que o modelo "decore" o jeito de se mover de alguém e dê resultado inflado.

- UI-PRMD (10 participantes): validação cruzada leave-one-subject-out (LOSO) ou `GroupKFold(5)`.
- KIMORE: `GroupShuffleSplit` estratificado por grupo clínico, ~20% dos participantes no teste.
- Vídeos próprios: sempre e só teste.
- REHAB24-6: só teste (ver [01](01-dados.md#rehab24-6-černek-sedmidubský-budíková--sisap-2024)).

## Cenários de avaliação

| Cenário | Treino | Teste | Pergunta respondida |
|---|---|---|---|
| A | UI-PRMD | UI-PRMD (participantes não vistos) | O modelo aprende correto × incorreto? |
| B | UI-PRMD + KIMORE | KIMORE (não vistos), separado em saudáveis × pacientes | Generaliza para pessoas com limitação real? (viés) |
| C | UI-PRMD + KIMORE | Vídeos próprios (webcam) | Funciona com câmera comum? (gap Kinect × webcam) |
| D | C + estimador trocado | Vídeos próprios com YOLO-pose | MediaPipe ou YOLO dá melhor resultado final? |
| ~~E~~ | — | — | Removido: a cópia acessível do KIMORE não tem vídeo RGB. A diferença Kinect × webcam é medida pelos cenários C e F. |
| F | UI-PRMD + KIMORE | REHAB24-6 (`squat` e `lateral_raise`) | Generaliza para pessoas e câmeras de fora do grupo? |

## Métricas

| Métrica | Onde | Meta |
|---|---|---|
| Acurácia, F1 macro, matriz de confusão | A–D e F, por modelo e por exercício | F1 macro ≥ 0,80 (META-01) |
| F1 separado saudáveis × pacientes | B | reportar diferença |
| Erro absoluto médio da contagem | Vídeos próprios e REHAB24-6 | ≤ 1 por série de 10 (META-02) |
| FPS do pipeline completo (captura + pose + atributos + classificador) | Notebook sem GPU dos integrantes | ≥ 15 (META-03) |
| Taxa de quadros com pose válida | Vídeos próprios, por condição | reportar ([07](07-testes-robustez.md)) |

Resultados com média ± desvio-padrão entre folds quando houver validação cruzada.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| AVA-01 | Funções de divisão por participante com teste que garante interseção vazia de `subject_id` entre treino e teste | DEVE |
| AVA-02 | Script `evaluate.py` que roda os cenários A–D e F e gera `reports/results.md` + figuras | DEVE |
| AVA-03 | Script de benchmark de FPS que reporta média e percentil 5 em 60 s de vídeo | DEVE |
| AVA-04 | Relatório final com: tabela RF × LSTM (× M3), análise de viés (B), análise Kinect × webcam (C, F), generalização externa (F), MediaPipe × YOLO (D), limitações | DEVE |
| AVA-05 | Análise de erros: exemplos de repetições mal classificadas e hipótese do motivo | PODE |

## Critérios de aceite

- `reports/results.md` gerado automaticamente por script, sem números colados à mão.
- Todas as metas META-01 a META-04 têm número medido no relatório, atingidas ou não (se não, com explicação).

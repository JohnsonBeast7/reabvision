# Resultados da avaliação

Gerado automaticamente por `python -m reabvision.models.evaluate` em 2026-11-24 19:46. Limiar de decisão fixo em 0.5.
Pessoas de teste nunca aparecem no treino. Meta: F1 macro ≥ 0,80.

## Cenário A — UI-PRMD, deixando uma pessoa de fora

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 200 | 0.828 | 0.830 |
| squat | todos | LSTM | 200 | 0.796 | 0.800 |
| lateral_raise | todos | RF | 200 | 0.990 | 0.990 |
| lateral_raise | todos | LSTM | 200 | 0.758 | 0.765 |
| front_raise | todos | RF | 200 | 0.920 | 0.920 |
| front_raise | todos | LSTM | 200 | 0.729 | 0.730 |

## Cenário B — KIMORE (pessoas não vistas), saudáveis × pacientes

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 66 | 0.557 | 0.636 |
| squat | paciente | RF | 31 | 0.184 | 0.226 |
| squat | todos | LSTM | 66 | 0.653 | 0.682 |
| squat | paciente | LSTM | 31 | 0.295 | 0.419 |
| front_raise | todos | RF | 88 | 0.760 | 0.761 |
| front_raise | saudavel | RF | 45 | 0.430 | 0.756 |
| front_raise | paciente | RF | 43 | 0.616 | 0.767 |
| front_raise | todos | LSTM | 88 | 0.613 | 0.614 |
| front_raise | saudavel | LSTM | 45 | 0.456 | 0.667 |
| front_raise | paciente | LSTM | 43 | 0.358 | 0.558 |

## Cenário F — REHAB24-6 (vídeo RGB, pessoas externas), por condição

_Pendente: F: poses do REHAB24-6 ainda não extraídas_

## Cenário C — vídeos próprios (MediaPipe)

_Pendente: C: vídeos próprios ainda não gravados_

## Cenário D — vídeos próprios (YOLO-pose)

_Pendente: D: vídeos próprios ainda não gravados_

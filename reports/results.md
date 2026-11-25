# Resultados da avaliação

Gerado automaticamente por `python -m reabvision.models.evaluate` em 2026-11-24 21:55. Limiar de decisão fixo em 0.5.
Pessoas de teste nunca aparecem no treino. Meta: F1 macro ≥ 0,80.

## Cenário A — UI-PRMD, deixando uma pessoa de fora

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 200 | 0.828 | 0.830 |
| squat | todos | LSTM | 200 | 0.796 | 0.800 |
| lateral_raise | todos | RF | 200 | 0.900 | 0.900 |
| lateral_raise | todos | LSTM | 200 | 0.740 | 0.740 |
| front_raise | todos | RF | 200 | 0.874 | 0.875 |
| front_raise | todos | LSTM | 200 | 0.731 | 0.735 |

## Cenário B — KIMORE (pessoas não vistas), saudáveis × pacientes

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 66 | 0.557 | 0.636 |
| squat | paciente | RF | 31 | 0.184 | 0.226 |
| squat | todos | LSTM | 66 | 0.653 | 0.682 |
| squat | paciente | LSTM | 31 | 0.295 | 0.419 |
| front_raise | todos | RF | 88 | 0.761 | 0.761 |
| front_raise | saudavel | RF | 45 | 0.577 | 0.778 |
| front_raise | paciente | RF | 43 | 0.597 | 0.744 |
| front_raise | todos | LSTM | 88 | 0.636 | 0.636 |
| front_raise | saudavel | LSTM | 45 | 0.550 | 0.689 |
| front_raise | paciente | LSTM | 43 | 0.368 | 0.581 |

## Cenário F — treino só com Kinect, teste no REHAB24-6 (vídeo RGB): diferença Kinect × webcam

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 382 | 0.312 | 0.364 |
| squat | orientation=front | RF | 191 | 0.375 | 0.408 |
| squat | orientation=side | RF | 191 | 0.242 | 0.319 |
| squat | lights_on=0 | RF | 98 | 0.222 | 0.224 |
| squat | lights_on=1 | RF | 284 | 0.331 | 0.412 |
| squat | extra_person=0 | RF | 299 | 0.295 | 0.368 |
| squat | extra_person=1 | RF | 47 | 0.268 | 0.277 |
| squat | extra_person=2 | RF | 34 | 0.393 | 0.412 |
| squat | todos | LSTM | 382 | 0.242 | 0.319 |
| squat | orientation=front | LSTM | 191 | 0.242 | 0.319 |
| squat | orientation=side | LSTM | 191 | 0.242 | 0.319 |
| squat | lights_on=0 | LSTM | 98 | 0.125 | 0.143 |
| squat | lights_on=1 | LSTM | 284 | 0.276 | 0.380 |
| squat | extra_person=0 | LSTM | 299 | 0.256 | 0.344 |
| squat | extra_person=1 | LSTM | 47 | 0.161 | 0.191 |
| squat | extra_person=2 | LSTM | 34 | 0.227 | 0.294 |
| lateral_raise | todos | RF | 356 | 0.400 | 0.520 |
| lateral_raise | orientation=front | RF | 139 | 0.461 | 0.540 |
| lateral_raise | orientation=half-profile | RF | 78 | 0.339 | 0.513 |
| lateral_raise | orientation=side | RF | 139 | 0.359 | 0.504 |
| lateral_raise | lights_on=0 | RF | 128 | 0.377 | 0.492 |
| lateral_raise | lights_on=1 | RF | 228 | 0.413 | 0.535 |
| lateral_raise | extra_person=0 | RF | 301 | 0.378 | 0.505 |
| lateral_raise | extra_person=1 | RF | 23 | 0.357 | 0.435 |
| lateral_raise | extra_person=2 | RF | 23 | 0.452 | 0.826 |
| lateral_raise | todos | LSTM | 356 | 0.326 | 0.365 |
| lateral_raise | orientation=front | LSTM | 139 | 0.215 | 0.216 |
| lateral_raise | orientation=half-profile | LSTM | 78 | 0.401 | 0.423 |
| lateral_raise | orientation=side | LSTM | 139 | 0.325 | 0.482 |
| lateral_raise | lights_on=0 | LSTM | 128 | 0.299 | 0.352 |
| lateral_raise | lights_on=1 | LSTM | 228 | 0.340 | 0.373 |
| lateral_raise | extra_person=0 | LSTM | 301 | 0.316 | 0.372 |
| lateral_raise | extra_person=1 | LSTM | 23 | 0.216 | 0.217 |
| lateral_raise | extra_person=2 | LSTM | 23 | 0.417 | 0.435 |

## Cenário F2 — treino com Kinect + REHAB24-6, testando cada pessoa do REHAB24-6 fora do treino

| Exercício | Grupo | Modelo | n | F1 macro | Acurácia |
|---|---|---|---|---|---|
| squat | todos | RF | 382 | 0.555 | 0.589 |
| squat | todos | LSTM | 382 | 0.509 | 0.510 |
| lateral_raise | todos | RF | 356 | 0.667 | 0.669 |
| lateral_raise | todos | LSTM | 356 | 0.685 | 0.691 |

## Cenários C e D — app completo nos vídeos próprios (C: MediaPipe, D: YOLO-pose)

Rótulos dos vídeos anotados por inspeção visual; erro de contagem por vídeo (meta ≤ 1 por série de 10).

| Exercício | Estimador | Avaliação | Vídeos | Erro de contagem (média / máx) | Reps casadas | Acurácia | F1 macro |
|---|---|---|---|---|---|---|---|
| front_raise | mediapipe | regras | 5 | 0.80 / 2 | 24 | 0.875 | — |
| lateral_raise | mediapipe | regras | 3 | 1.00 / 2 | 20 | 0.850 | 0.657 |
| squat | mediapipe | regras | 1 | 0.00 / 0 | 9 | 1.000 | — |
| front_raise | mediapipe | rf | 5 | 0.80 / 2 | 24 | 0.000 | — |
| lateral_raise | mediapipe | rf | 3 | 1.00 / 2 | 20 | 0.300 | 0.231 |
| squat | mediapipe | rf | 1 | 0.00 / 0 | 9 | 1.000 | — |
| front_raise | yolo | regras | 5 | 1.20 / 2 | 24 | 0.792 | — |
| lateral_raise | yolo | regras | 3 | 1.67 / 4 | 19 | 0.895 | 0.721 |
| squat | yolo | regras | 1 | 0.00 / 0 | 9 | 1.000 | — |
| front_raise | yolo | rf | 5 | 1.20 / 2 | 24 | 0.000 | — |
| lateral_raise | yolo | rf | 3 | 1.67 / 4 | 19 | 0.105 | 0.095 |
| squat | yolo | rf | 1 | 0.00 / 0 | 9 | 1.000 | — |

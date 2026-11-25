# Robustez — own

Gerado por `python -m reabvision.robustness.robustness`.

## Por degradação sintética

| degradacao | estimador | detecção | tremor (°/quadro) | erro de contagem | FPS |
|---|---|---|---|---|---|
| base | mediapipe | 97% | 1.47 | 1.00 | 56 |
| base | yolo | 95% | 1.73 | 0.67 | 24 |
| desfoque_15 | mediapipe | 97% | 1.39 | 0.67 | 51 |
| desfoque_31 | mediapipe | 97% | 1.45 | 1.00 | 44 |
| escuro_12 | mediapipe | 94% | 1.54 | 0.67 | 52 |
| escuro_25 | mediapipe | 96% | 1.47 | 0.67 | 52 |
| longe_25 | mediapipe | 94% | 1.48 | 0.67 | 47 |
| longe_40 | mediapipe | 99% | 1.36 | 0.67 | 47 |
| resolucao_160 | mediapipe | 97% | 1.48 | 0.67 | 51 |
| resolucao_96 | mediapipe | 97% | 1.41 | 0.67 | 52 |
| ruido_35 | mediapipe | 85% | 1.67 | 2.33 | 29 |
| ruido_60 | mediapipe | 64% | 2.46 | 3.33 | 29 |

## Condição de gravação (vídeos originais)

| condicao | estimador | detecção | tremor | erro de contagem | FPS |
|---|---|---|---|---|---|
| C05 | mediapipe | 97% | 1.47 | 1.00 | 56 |
| C05 | yolo | 95% | 1.73 | 0.67 | 24 |

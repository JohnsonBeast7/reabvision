# Robustez — rehab24

Gerado por `python -m reabvision.robustness.robustness`.

## Por degradação sintética

| degradacao | estimador | detecção | tremor (°/quadro) | erro de contagem | FPS |
|---|---|---|---|---|---|
| base | mediapipe | 75% | 0.48 | 4.00 | 47 |

## Luz (REHAB24-6) (vídeos originais)

| luz | estimador | detecção | tremor | erro de contagem | FPS |
|---|---|---|---|---|---|
| apagada | mediapipe | 75% | 0.48 | 4.00 | 47 |

## Pessoa extra na cena (vídeos originais)

| pessoa_extra | estimador | detecção | tremor | erro de contagem | FPS |
|---|---|---|---|---|---|
| False | mediapipe | 67% | 0.38 | 4.67 | 47 |
| True | mediapipe | 100% | 0.68 | 2.00 | 46 |

## Orientação da câmera (vídeos originais)

| orientacao | estimador | detecção | tremor | erro de contagem | FPS |
|---|---|---|---|---|---|
| front | mediapipe | 100% | 0.48 | 4.25 | 47 |
| side | mediapipe | 50% | 0.47 | 3.75 | 47 |

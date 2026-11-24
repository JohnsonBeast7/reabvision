# 02 — Estimativa de pose e atributos

## Estimadores de pose

Os estimadores ficam atrás de uma interface comum, para trocar um pelo outro sem mexer no resto:

```python
class PoseEstimator(Protocol):
    name: str
    def process(self, frame_bgr: np.ndarray) -> PoseResult | None: ...

@dataclass
class PoseResult:
    joints: np.ndarray      # (12, 3) no esqueleto comum; z = NaN se só 2D
    visibility: np.ndarray  # (12,) confiança 0..1
    is_3d: bool
    raw: Any                # saída original, para desenhar o overlay
```

### MediaPipe BlazePose (padrão)

- 33 pontos por quadro, roda em CPU em tempo real. Não é treinado pelo grupo.
- Usa `pose_world_landmarks` (metros, centrado no quadril) para os ângulos → `is_3d = True`.
- `model_complexity` configurável (0/1/2); padrão 1. Medir FPS de cada um em [07](07-testes-robustez.md).

### YOLO-pose (alternativa, sugestão do professor)

- Ultralytics YOLO (v8/11) na variante `-pose`, que detecta a pessoa e estima **17 pontos COCO**.
- Os 17 pontos COCO incluem exatamente as 12 articulações do esqueleto comum, então o resto do pipeline não muda.
- Só 2D (`is_3d = False`); ângulos calculados no plano da imagem.
- Vantagens esperadas: detector robusto de pessoa (fundo poluído, pessoa pequena/longe). Desvantagens: sem profundidade, possivelmente mais lento em CPU — por isso usar o modelo `n` (nano).
- Nota: YOLO "puro" é detector de objetos (caixas), não diz se o movimento está correto. Ele entra aqui como estimador de pose (variante `-pose`) e, opcionalmente, como detector de pessoa para recortar a imagem antes do MediaPipe quando a pessoa estiver longe.
- Licença AGPL-3.0 do Ultralytics: compatível com repositório público acadêmico; registrar no README.

## Mapeamento para o esqueleto comum

| Comum | MediaPipe (índice) | COCO/YOLO (índice) | Kinect v2 |
|---|---|---|---|
| l_shoulder | 11 | 5 | ShoulderLeft |
| r_shoulder | 12 | 6 | ShoulderRight |
| l_elbow | 13 | 7 | ElbowLeft |
| r_elbow | 14 | 8 | ElbowRight |
| l_wrist | 15 | 9 | WristLeft |
| r_wrist | 16 | 10 | WristRight |
| l_hip | 23 | 11 | HipLeft |
| r_hip | 24 | 12 | HipRight |
| l_knee | 25 | 13 | KneeLeft |
| r_knee | 26 | 14 | KneeRight |
| l_ankle | 27 | 15 | AnkleLeft |
| r_ankle | 28 | 16 | AnkleRight |

Atenção: confirmar se "left" é o lado do paciente ou da imagem em cada fonte (MediaPipe usa o lado do paciente; imagem de webcam costuma ser espelhada). Teste unitário DEVE cobrir isso.

## Atributos

### Ângulos articulares (por quadro)

Ângulo no vértice B entre os segmentos BA e BC. Lista fixa:

| Atributo | A – B – C |
|---|---|
| knee_l / knee_r | quadril – joelho – tornozelo |
| hip_l / hip_r | ombro – quadril – joelho |
| elbow_l / elbow_r | ombro – cotovelo – punho |
| shoulder_l / shoulder_r | quadril – ombro – cotovelo |
| trunk_tilt | inclinação do vetor (meio dos quadris → meio dos ombros) em relação à vertical |
| knee_valgus_l / _r (PODE) | desvio do joelho em relação à linha quadril–tornozelo no plano frontal |

### Ângulo principal por exercício (usado na contagem)

| Exercício | Ângulo principal |
|---|---|
| squat | média de knee_l e knee_r |
| lateral_raise | média de shoulder_l e shoulder_r |
| front_raise | média de shoulder_l e shoulder_r |

### Atributos por repetição (entrada do Random Forest)

Para cada ângulo, dentro da janela da repetição: mínimo, máximo, amplitude, média, desvio-padrão, velocidade angular média e máxima (em módulo), duração da repetição, e assimetria esquerda–direita (diferença média entre pares l/r).

### Sequência por repetição (entrada da LSTM)

Matriz `(T_fixo, n_ângulos)` da repetição reamostrada para `T_fixo = 64` quadros, normalizada por z-score com estatísticas do treino.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| POS-01 | Interface `PoseEstimator` + implementação MediaPipe | DEVE |
| POS-02 | Implementação YOLO-pose atrás da mesma interface | DEVE (para a comparação pedida pelo professor) |
| POS-03 | Função de mapeamento de cada fonte para o esqueleto comum, com testes | DEVE |
| POS-04 | Suavização temporal leve dos pontos (média móvel ou filtro One-Euro), configurável | DEVE |
| POS-05 | Quadros com visibilidade média < 0,5 nas articulações do exercício são marcados como inválidos e não alimentam contagem/classificação | DEVE |
| FEA-01 | Função `compute_angles(joints) -> DataFrame` com a lista fixa acima, testada com poses sintéticas de ângulo conhecido (ex.: 90°, 180°) | DEVE |
| FEA-02 | Função de atributos por repetição (RF) | DEVE |
| FEA-03 | Função de sequência por repetição (LSTM) | DEVE |
| FEA-04 | Mesmo código de atributos usado no treino (Kinect) e no app (webcam) — sem duplicação | DEVE |
| FEA-05 | Comparação visual das distribuições de ângulos Kinect × MediaPipe × YOLO para o mesmo exercício | DEVE |

## Critérios de aceite

- Testes unitários de ângulo passam com tolerância de 1°.
- Rodar MediaPipe e YOLO-pose sobre o mesmo vídeo próprio gera dois `DataFrame` de ângulos com as mesmas colunas.
- Gráfico de FEA-05 existe no relatório.

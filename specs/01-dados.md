# 01 — Dados

## Fontes

### UI-PRMD (Vakanski et al., 2018)

- 10 exercícios, 10 voluntários saudáveis, 10 repetições corretas + 10 incorretas por exercício.
- Captura com Vicon e Kinect. **Usamos o Kinect** (mais próximo de uma câmera comum).
- Papel: **fonte principal de treino** de correto × incorreto (tem rótulo explícito).
- Exercícios usados (D1): m01 agachamento profundo, m07 "standing shoulder abduction" (= elevação lateral de braço), m10 escapção/elevação de ombro em pé (mais próximo da elevação frontal — confirmar).
- Download: o site oficial (webpages.uidaho.edu/ui-prmd) saiu do ar em 2025. Os arquivos originais estão no Internet Archive: `Segmented Movements.zip` (corretas) e `Incorrect Segmented Movements.zip` (incorretas), ~200 MB cada, em `http://web.archive.org/web/2025id_/https://webpages.uidaho.edu/ui-prmd/<arquivo>`. Licença CC BY 4.0; citar Vakanski et al. (2018).

### KIMORE (Capecci et al., 2019)

- 5 exercícios de coluna e tronco, 78 participantes (saudáveis e pacientes com dor lombar, AVC, Parkinson), Kinect v2, pontuações clínicas de especialistas.
- Papel: **ampliar diversidade e avaliar em pessoas com limitação real**.
- Exercícios usados (D1): Es5 agachamento, Es1 elevação de braços.
- Rótulo binário (D7): repetição/série é "correta" se a pontuação clínica do exercício ≥ limiar. O limiar DEVE ser definido olhando a distribuição das pontuações (sugestão inicial: mediana dos participantes saudáveis menos 1 desvio-padrão) e registrado em `configs/`.
- Grupo do participante (saudável × paciente) é guardado como metadado para análise de viés ([05](05-avaliacao.md)).
- Download: a página oficial (vrai.dii.univpm.it) e o link do SharePoint da universidade estão fora do ar (nov/2026). Usamos uma cópia dos arquivos originais publicada no Google Drive por terceiros (pasta `1b1anGzSytePiCUyoz8AlGMV2G54e_ZeC`), com a mesma estrutura `CG|GPP/<grupo>/<sujeito>/Es<n>/{Raw,Label}`. Baixamos só Es1 e Es5: `Raw/JointPosition*.csv`, `Raw/TimeStamp*.csv` e `Label/*.xlsx`.
- Essa cópia **não tem o vídeo RGB** (só profundidade), então a comparação Kinect × webcam no mesmo movimento (antigo cenário E) foi removida ([05](05-avaliacao.md)).

### REHAB24-6 (Černek, Sedmidubský, Budíková — SISAP 2024)

- 65 gravações de 10 adultos saudáveis, 30 FPS, **vídeo RGB de duas câmeras** (horizontal e vertical), sequências de esqueleto, segmentação por repetição e rótulo **correto/incorreto por repetição** (orientado por fisioterapeuta: ≥ 5 corretas e ≥ 5 incorretas por série). ~1.057 repetições após filtragem.
- 6 exercícios: abdução de braço, "arm VW", flexão na mesa, abdução de perna, avanço e agachamento. **Dois coincidem com os nossos**: abdução de braço = `lateral_raise` e agachamento = `squat`. Não há equivalente da elevação frontal.
- Papel: **teste externo com câmera RGB comum e pessoas de fora do grupo** (cenário F em [05](05-avaliacao.md)) e teste extra do contador (tem segmentação por repetição). Como roda MediaPipe/YOLO sobre o vídeo, é o conjunto mais parecido com o uso real.
- Uso no treino PODE ser testado depois (com divisão por participante), mas só se o desempenho no cenário C ficar abaixo da meta — para manter o teste limpo.
- Disponível no Zenodo (DOI 10.5281/zenodo.13305826), acesso aberto. Licença **CC BY-NC 4.0**: uso acadêmico não comercial permitido, citação obrigatória do artigo (Černek; Sedmidubský; Budíková. *REHAB24-6: Physical Therapy Dataset for Analyzing Pose Estimation Methods*. SISAP 2024). Compatível com o projeto.
- Arquivos necessários: `videos.zip` (2,7 GB) e `Segmentation.csv`. Os demais (`2d/3d_joints`, `2d/3d_markers`, ~3 GB) PODEM ser baixados para comparar o esqueleto de referência com o MediaPipe/YOLO.

### Bases consideradas e não adotadas

| Base | Motivo |
|---|---|
| Fitness-AQA (Parmar et al., 2022) | Agachamento com barra em academia, gravação livre; movimento diferente do agachamento de reabilitação. Uso só não comercial. Pode servir de inspiração para tipos de erro do agachamento |
| RepCount-A (TransRAC, CVPR 2022) | Vídeos variados com contagem anotada, mas sem rótulo de correção e com poucos exercícios iguais aos nossos. PODE complementar o teste do contador com os vídeos de agachamento |

### Vídeos próprios do grupo

- ~10 vídeos por exercício, gravados pelos integrantes, com execuções corretas e incorretas.
- Papel: **somente teste** em condições reais (nunca usados no treino) e base dos testes de robustez ([07](07-testes-robustez.md)).
- Continuam necessários mesmo com REHAB24-6 e o RGB do KIMORE: só eles têm **condições de captura controladas** (mesma pessoa, variando luz, câmera, distância), a elevação frontal e o ambiente real da demonstração.
- Cada vídeo tem anotação manual: exercício, número real de repetições, rótulo de cada repetição (correta/incorreta e tipo de erro), condição de gravação.
- Guarda e descarte: ver [09](09-etica-privacidade.md).

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| DAT-01 | Script de download/organização que coloca os dados brutos em `data/raw/<dataset>/` e documenta a origem e as condições de uso | DEVE |
| DAT-02 | `data/` fica fora do git (`.gitignore`), exceto arquivos de anotação dos vídeos próprios sem imagem | DEVE |
| DAT-03 | Loader de UI-PRMD que converte para o formato canônico | DEVE |
| DAT-04 | Loader de KIMORE que converte para o formato canônico, incluindo pontuação clínica e grupo | DEVE |
| DAT-05 | Extrator que roda o estimador de pose sobre os vídeos próprios e salva no formato canônico (sem salvar quadros de imagem) | DEVE |
| DAT-06 | Mapeamento de articulações Kinect v1/v2 → esqueleto comum documentado em código e testado | DEVE |
| DAT-07 | Arquivo de anotação dos vídeos próprios (`data/own/annotations.csv`) com o esquema abaixo | DEVE |
| DAT-08 | Relatório exploratório (notebook) com contagem de amostras por exercício, rótulo, participante e grupo | DEVE |
| DAT-09 | Reamostragem temporal para uma taxa comum (30 Hz) | DEVE |
| DAT-10 | Loader de REHAB24-6: roda o estimador de pose sobre os vídeos RGB e converte para o formato canônico com rótulo por repetição | DEVE |
| DAT-11 | ~~Extração de pose sobre o vídeo RGB do KIMORE~~ — removido: a cópia acessível não tem RGB | — |

## Formato canônico

Uma sequência = uma série de um participante em um exercício.

```python
@dataclass
class Sequence:
    dataset: str            # "uiprmd" | "kimore" | "rehab24" | "own"
    subject_id: str         # único por dataset, ex.: "uiprmd_s03"
    exercise: str           # "squat" | "lateral_raise" | "front_raise"
    joints: np.ndarray      # (T, 12, 3) em metros ou coords normalizadas; NaN se ausente
    fps: float              # 30 após reamostragem
    label: int | None       # 1 = correta, 0 = incorreta (série inteira ou por rep)
    rep_labels: list[int] | None   # rótulo por repetição, quando existir
    meta: dict              # grupo clínico, pontuação, condição de gravação etc.
```

Ordem fixa das 12 articulações (índice → nome), usada em todo o projeto:

```
0 l_shoulder  1 r_shoulder  2 l_elbow  3 r_elbow  4 l_wrist  5 r_wrist
6 l_hip       7 r_hip       8 l_knee   9 r_knee   10 l_ankle 11 r_ankle
```

Sequências processadas são salvas em `data/processed/<dataset>.parquet` (ou `.npz`), para não reprocessar a cada experimento.

## Esquema de `annotations.csv` (vídeos próprios)

| coluna | exemplo |
|---|---|
| `video_id` | `squat_joao_01` |
| `subject_id` | `own_joao` |
| `exercise` | `squat` |
| `n_reps_real` | `10` |
| `rep_labels` | `1;1;0;1;...` |
| `error_type` | `joelho_valgo` / `amplitude_curta` / vazio |
| `condition_id` | `C00` (ver [07](07-testes-robustez.md)) |
| `camera` | `webcam_notebook_720p` |
| `notes` | texto livre |

## Critérios de aceite

- Os três loaders produzem `Sequence` válidas; teste unitário com um arquivo de amostra pequeno de cada dataset.
- Notebook exploratório roda do início ao fim e mostra a tabela de contagens.
- Nenhum vídeo ou quadro de imagem é versionado no git.

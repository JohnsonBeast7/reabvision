# 07 — Testes de robustez (condições de captura)

Pedido explícito do professor: variar iluminação, câmera e outros fatores que possam atrapalhar o modelo, **e especificar essas condições**. Esta spec define quais condições, como gravar e o que medir.

## Desenho do experimento

Para caber no prazo, **um fator por vez** a partir de uma condição base (não fatorial completo). As condições vêm de três fontes, para reduzir a gravação própria:

1. **Vídeos próprios** (27 vídeos): condição base com 5 integrantes e as condições que nenhuma outra fonte cobre (tipo de câmera, distância, roupa, oclusão).
2. **REHAB24-6** ([01](01-dados.md)): pessoas de fora do grupo, com metadados de **luz acesa/apagada**, **pessoa extra na câmera** e **orientação da câmera** (frente/lado) em `Segmentation.csv`. Cobre agachamento e elevação lateral.
3. **Degradação sintética** (OpenCV) aplicada aos vídeos base: escurecimento, resolução reduzida, ruído e desfoque.

**Condição base (C00)**: sala bem iluminada com luz frontal/difusa, webcam do notebook em 720p, câmera na altura da cintura, pessoa a ~2,5 m, fundo neutro, roupa justa ou de academia, sem oclusão, velocidade normal. Enquadramento: corpo inteiro no agachamento; da cabeça até o meio das coxas nas elevações, com espaço para os braços abertos.

## Matriz de condições

| ID | Fator | Variação em relação à base | Fonte |
|---|---|---|---|
| C00 | Base | — | Própria (5 pessoas) + REHAB24-6 |
| C01 | Iluminação | Pouca luz | REHAB24-6 (`lights_on = 0`) + sintética (escurecimento) |
| C02 | Iluminação | Contraluz (janela ou luz forte atrás da pessoa) | Não coberta (PODE gravar) |
| C03 | Iluminação | Luz lateral forte | Não coberta (PODE gravar) |
| C04 | Câmera | Resolução baixa (480p ou menos) | Sintética (redução de resolução) |
| C05 | Câmera | Celular como webcam | Própria |
| C06 | Câmera | Webcam externa USB diferente | Não coberta (PODE gravar) |
| C07 | Distância | Perto (~1,5 m) | Não coberta (PODE gravar) |
| C08 | Distância | Longe (~4 m) | Própria |
| C09 | Ângulo | Câmera a 45° / vista trocada | REHAB24-6 (`cam17_orientation` e câmera 18) |
| C12 | Fundo | Fundo poluído | Não coberta (PODE gravar) |
| C13 | Fundo | Outra pessoa ao fundo | REHAB24-6 (`extra_person_in_cam17/18`) |
| C14 | Roupa | Roupa larga (moletom, calça larga) | Própria |
| C15 | Oclusão | Objeto (cadeira, mesa) cobrindo parte das pernas | Própria |
| C18 | Qualidade | Ruído e desfoque de imagem | Sintética |

Posição da câmera recomendada por exercício (registrar na condição base):

| Exercício | Vista base | Motivo |
|---|---|---|
| squat | lateral (ou 45°) | ângulo do joelho e do tronco aparece melhor de lado |
| lateral_raise | frontal | movimento no plano frontal |
| front_raise | lateral (ou 45°) | movimento no plano sagital |

## Protocolo de gravação (vídeos próprios)

Cada vídeo: **uma pessoa, um exercício, 10 repetições** (~7 corretas e ~3 incorretas de propósito, misturadas e anotadas), parado 2 s no começo e no fim.

| Pessoa | Vídeos | Condições (sempre os 3 exercícios) |
|---|---|---|
| A | 6 | C00 + C05 (celular) |
| B | 6 | C00 + C08 (longe) |
| C | 6 | C00 + C14 (roupa larga) |
| D | 6 | C00 + C15 (oclusão das pernas) |
| E | 3 | C00 |
| **Total** | **27** | |

- Cada vídeo entra em `annotations.csv` com seu `condition_id` ([01](01-dados.md)).
- Nome do arquivo: `<exercicio>_<pessoa>_<condicao>.mp4`.
- Os vídeos ficam fora do git, em pasta restrita ao grupo ([09](09-etica-privacidade.md)).

## Métricas por condição

| Métrica | Descrição |
|---|---|
| Taxa de detecção | % de quadros com pose válida (visibilidade ≥ 0,5) |
| Estabilidade | desvio-padrão quadro a quadro do ângulo principal em repouso (tremor) |
| Erro de contagem | |contadas − reais| |
| F1 macro | classificação das repetições |
| FPS | do pipeline completo |

Cada métrica é calculada para **MediaPipe e YOLO-pose** — é aqui que a sugestão do YOLO é testada na prática.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| ROB-01 | Matriz de condições versionada em `configs/conditions.yaml` (esta tabela) | DEVE |
| ROB-02 | Gravar os 27 vídeos próprios do protocolo acima (C00, C05, C08, C14, C15) | DEVE |
| ROB-03 | Gravar as condições marcadas como não cobertas | PODE |
| ROB-04 | Script `robustness.py` que roda os dois estimadores sobre os vídeos próprios, o REHAB24-6 (agrupado pelos metadados de condição) e as versões sintéticas, e gera tabela condição × métrica e gráfico de queda relativa à base | DEVE |
| ROB-05 | Seção no relatório: quais condições mais degradam, recomendações de uso (ex.: "evite contraluz") que viram texto de instrução no app | DEVE |
| ROB-06 | Degradação sintética: aplicar aos vídeos base escurecimento, redução de resolução, ruído e desfoque via OpenCV, em níveis crescentes, e medir as mesmas métricas | DEVE |

## Critérios de aceite

- Tabela condição × métrica × estimador presente em `reports/`.
- Instruções de posicionamento e iluminação do app ([06](06-aplicacao.md)) baseadas nos resultados.

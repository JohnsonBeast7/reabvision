# 07 — Testes de robustez (condições de captura)

Pedido explícito do professor: variar iluminação, câmera e outros fatores que possam atrapalhar o modelo, **e especificar essas condições**. Esta spec define quais condições, como gravar e o que medir.

## Desenho do experimento

Para caber no prazo, **um fator por vez** a partir de uma condição base (não fatorial completo).

**Condição base (C00)**: sala bem iluminada com luz frontal/difusa, webcam do notebook em 720p, câmera na altura do quadril, pessoa a ~2,5 m com corpo inteiro no quadro, vista frontal (lateral para o agachamento — ver abaixo), fundo neutro, roupa justa ou de academia, sem oclusão, velocidade normal.

## Matriz de condições

| ID | Fator | Variação em relação à base |
|---|---|---|
| C00 | Base | — |
| C01 | Iluminação | Pouca luz (só luz de teto fraca / ambiente à noite) |
| C02 | Iluminação | Contraluz (janela ou luz forte atrás da pessoa) |
| C03 | Iluminação | Luz lateral forte (metade do corpo na sombra) |
| C04 | Câmera | Resolução baixa (480p) |
| C05 | Câmera | Celular como webcam (DroidCam/Iriun ou vídeo gravado no celular) |
| C06 | Câmera | Webcam externa USB diferente |
| C07 | Distância | Perto (~1,5 m, pés ou cabeça podem sair do quadro) |
| C08 | Distância | Longe (~4 m) |
| C09 | Ângulo | Câmera a 45° |
| C10 | Ângulo | Vista trocada (lateral nos exercícios de braço / frontal no agachamento) |
| C11 | Altura da câmera | Câmera no chão ou acima da cabeça |
| C12 | Fundo | Fundo poluído (móveis, objetos, cores parecidas com a roupa) |
| C13 | Fundo | Outra pessoa passando ou parada ao fundo |
| C14 | Roupa | Roupa larga (moletom, calça larga) |
| C15 | Oclusão | Objeto (cadeira, mesa) cobrindo parte das pernas |
| C16 | Velocidade | Execução muito rápida |
| C17 | Velocidade | Execução muito lenta |

Posição da câmera recomendada por exercício (registrar na condição base):

| Exercício | Vista base | Motivo |
|---|---|---|
| squat | lateral (ou 45°) | ângulo do joelho e do tronco aparece melhor de lado |
| lateral_raise | frontal | movimento no plano frontal |
| front_raise | lateral (ou 45°) | movimento no plano sagital |

## Protocolo de gravação

- Cada condição: pelo menos **2 integrantes diferentes** × **1 série de 10 reps** por exercício, com algumas repetições propositalmente incorretas (anotadas).
- Base C00 com mais participantes (todos que puderem), pois também serve como teste geral ([05](05-avaliacao.md) cenário C).
- Diversidade entre integrantes (altura, biotipo) registrada em `notes`, sem dados identificáveis além do ID.
- Cada vídeo entra em `annotations.csv` com seu `condition_id` ([01](01-dados.md)).
- Lista de checagem impressa durante a gravação para não esquecer de anotar reps incorretas.

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
| ROB-02 | Gravar C00 e pelo menos C01, C02, C04, C05, C07, C08, C09, C12, C13, C14, C15 | DEVE |
| ROB-03 | Demais condições | PODE |
| ROB-04 | Script `robustness.py` que roda os dois estimadores sobre todos os vídeos e gera tabela condição × métrica e gráfico de queda relativa à base | DEVE |
| ROB-05 | Seção no relatório: quais condições mais degradam, recomendações de uso (ex.: "evite contraluz") que viram texto de instrução no app | DEVE |
| ROB-06 | Teste de robustez sintético PODE complementar: aplicar ao vídeo base escurecimento, ruído, blur e redução de resolução via OpenCV e medir as mesmas métricas | PODE |

## Critérios de aceite

- Tabela condição × métrica × estimador presente em `reports/`.
- Instruções de posicionamento e iluminação do app ([06](06-aplicacao.md)) baseadas nos resultados.

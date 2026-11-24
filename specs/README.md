# Specs — Monitoramento de Exercícios de Reabilitação por Visão Computacional

Especificações do projeto do Grupo 5, derivadas do [pré-projeto](../docs/pre-projeto/pre-projeto-grupo5.pdf) e do [comentário do professor](../docs/pre-projeto/comentario-professor.md).

As tarefas derivadas estão em [`todos/`](../todos/README.md).

Cada spec descreve **o que** deve ser construído e **como saber que está pronto** (critérios de aceite). Os requisitos têm IDs (`DAT-01`, `MOD-03`, ...) para serem referenciados nos To-dos e nos commits.

## Índice

| # | Spec | Assunto |
|---|---|---|
| 00 | [Visão geral](00-visao-geral.md) | Objetivo, escopo, arquitetura, decisões e metas |
| 01 | [Dados](01-dados.md) | UI-PRMD, KIMORE, vídeos próprios, formato canônico |
| 02 | [Pose e atributos](02-pose-e-features.md) | MediaPipe, YOLO-pose, articulações comuns, ângulos |
| 03 | [Contagem de repetições](03-contagem-repeticoes.md) | Picos e vales, segmentação das repetições |
| 04 | [Modelos](04-modelos.md) | Random Forest, LSTM, alternativa leve, treino |
| 05 | [Avaliação](05-avaliacao.md) | Divisão por participante, métricas, relatório |
| 06 | [Aplicação](06-aplicacao.md) | App Streamlit local com webcam e feedback |
| 07 | [Testes de robustez](07-testes-robustez.md) | Iluminação, câmera, distância, ângulo, fundo, oclusão |
| 08 | [Infra e execução local](08-infra-execucao-local.md) | Estrutura do repo, ambiente, testes automatizados, CI |
| 09 | [Ética e privacidade](09-etica-privacidade.md) | LGPD, privacidade, avisos, viés |

## Ordem sugerida de implementação

1. `08` (esqueleto do repo e ambiente) →
2. `01` + `02` (dados e atributos) →
3. `03` (contagem) →
4. `04` + `05` (modelos e avaliação) →
5. `06` (app) →
6. `07` (robustez, com os vídeos próprios) →
7. `09` em paralelo, desde o início.

## Convenções

- **DEVE** = obrigatório para a entrega. **PODE** = desejável, fazer se houver tempo.
- Decisões tomadas e em aberto ficam registradas em [00-visao-geral.md](00-visao-geral.md#decisões).

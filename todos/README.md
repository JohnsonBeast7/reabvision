# To-dos

Tarefas derivadas das [specs](../specs/README.md). Um arquivo por spec, com a mesma numeração. Cada tarefa cita o ID do requisito entre parênteses (ex.: `DAT-03`), para rastrear até a spec.

## Como usar

- Marque `[x]` ao concluir e coloque o nome de quem fez: `- [x] Loader UI-PRMD (DAT-03) — @fulano`.
- Para assumir uma tarefa, escreva o nome antes de começar: `- [ ] Loader UI-PRMD (DAT-03) — @fulano`.
- Tarefas marcadas com **(PODE)** são opcionais: só depois que as obrigatórias da mesma fase estiverem prontas.
- Commits citam o ID: `feat(data): loader UI-PRMD (DAT-03)`.

## Arquivos

| # | Arquivo | Spec |
|---|---|---|
| 00 | [Organização](00-organizacao.md) | [00](../specs/00-visao-geral.md) |
| 01 | [Dados](01-dados.md) | [01](../specs/01-dados.md) |
| 02 | [Pose e atributos](02-pose-e-features.md) | [02](../specs/02-pose-e-features.md) |
| 03 | [Contagem de repetições](03-contagem-repeticoes.md) | [03](../specs/03-contagem-repeticoes.md) |
| 04 | [Modelos](04-modelos.md) | [04](../specs/04-modelos.md) |
| 05 | [Avaliação](05-avaliacao.md) | [05](../specs/05-avaliacao.md) |
| 06 | [Aplicação](06-aplicacao.md) | [06](../specs/06-aplicacao.md) |
| 07 | [Testes de robustez](07-testes-robustez.md) | [07](../specs/07-testes-robustez.md) |
| 08 | [Infra e execução local](08-infra-execucao-local.md) | [08](../specs/08-infra-execucao-local.md) |
| 09 | [Ética e privacidade](09-etica-privacidade.md) | [09](../specs/09-etica-privacidade.md) |
| 10 | [Documentação e apresentação](10-documentacao-apresentacao.md) | — (cronograma do pré-projeto) |

## Fases (cronograma de 10 semanas do pré-projeto)

| Semanas | Fase | Arquivos principais |
|---|---|---|
| 1 | Pesquisa e estudo, organização | 00, 08 (esqueleto), 09 (termos) |
| 2–3 | Preparação dos dados | 01, 02 |
| 3–4 | Gravação dos vídeos próprios | 07 (gravação), 01 (anotação) |
| 4–6 | Contagem e treinamento dos modelos | 03, 04 |
| 6–7 | Implementação do app e avaliação | 05, 06 |
| 7–8 | Robustez e automação da produção | 07 (análise), 08 (CI) |
| 9 | Documentação | 10 |
| 10 | Preparação e apresentação | 10 |

## Dependências principais

- `02` depende do formato canônico de `01` (`DAT-03`/`DAT-04`).
- `03`, `04` dependem de `02` (ângulos).
- `05` depende de `04` e dos vídeos gravados em `07`.
- `06` depende de `02`, `03` e de pelo menos um modelo de `04`.
- Gravação (`07`) depende dos termos assinados (`09`).

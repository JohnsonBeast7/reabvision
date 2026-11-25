# 00 — Visão geral

## Problema

Boa parte da fisioterapia é feita em casa, sem supervisão. O paciente perde adesão e pode executar os movimentos errado. O sistema oferece um "olhar" automatizado usando só uma câmera comum, **como apoio ao fisioterapeuta, não como substituto**.

## Objetivo

Sistema que, pela webcam do computador, para cada um de 3 exercícios de reabilitação:

1. estima a pose do paciente quadro a quadro;
2. conta as repetições;
3. classifica cada repetição como **correta** ou **incorreta**;
4. mostra esse feedback em tempo real sobre o vídeo.

## Escopo

**Dentro**

- 3 exercícios (ver [D1](#decisões)).
- Treino com dados públicos de esqueleto (UI-PRMD e KIMORE) e validação com vídeos gravados pelo grupo.
- Comparação documentada entre Random Forest e LSTM (e uma alternativa leve, ver [04](04-modelos.md)).
- Estudo de robustez com variação controlada de iluminação, câmera, distância etc. ([07](07-testes-robustez.md)).
- App que roda **localmente** em notebook sem GPU, para a demonstração em sala.

**Fora**

- Diagnóstico, prescrição ou pontuação clínica.
- Treinar modelo de estimativa de pose (usamos pré-treinados).
- Reconhecer automaticamente qual exercício está sendo feito (o usuário escolhe na interface; ver [D3](#decisões)).
- Múltiplas pessoas simultâneas na cena.
- App mobile nativo.

## Arquitetura

```
 Webcam ──► Estimador de pose ──► Esqueleto comum ──► Ângulos ──┬──► Contador de repetições
 (OpenCV)   (MediaPipe BlazePose   (12 articulações)  articulares │       │ (início/fim de cada rep)
             ou YOLO-pose)                                        │       ▼
                                                                  └──► Classificador (RF / LSTM)
                                                                          │ correta × incorreta
                                                                          ▼
                                                              Interface Streamlit (overlay + placar)

 Offline: UI-PRMD / KIMORE ──► mesmo pipeline de ângulos ──► treino e avaliação dos modelos
```

O ponto central do desenho: **dados de treino (Kinect) e dados de uso (webcam) passam pelo mesmo extrator de atributos**, que trabalha só com o subconjunto comum de articulações e com ângulos (independentes de escala e posição).

## Metas (do pré-projeto)

| ID | Meta | Como medir |
|---|---|---|
| META-01 | F1 macro ≥ 0,80 em correto × incorreto, em participantes não vistos no treino | [05](05-avaliacao.md) |
| META-02 | Erro absoluto médio ≤ 1 repetição por série de 10 | [03](03-contagem-repeticoes.md), [05](05-avaliacao.md) |
| META-03 | ≥ 15 FPS em notebook sem GPU | [05](05-avaliacao.md), [07](07-testes-robustez.md) |
| META-04 | Comparação documentada RF × LSTM, com análise de viés e da diferença Kinect × webcam | [05](05-avaliacao.md) |
| META-05 | Protótipo funcional demonstrável em sala | [06](06-aplicacao.md) |
| META-06 | Repositório público com código, testes automatizados e documentação de uso | [08](08-infra-execucao-local.md) |

## Decisões

| ID | Decisão | Status | Motivo |
|---|---|---|---|
| D1 | Exercícios: **agachamento profundo**, **elevação lateral de braço** (abdução de ombro) e **elevação frontal de braço** (flexão de ombro) | Tomada. Mapeamento conferido nos dados: m01/Es5 e m07 batem; para a elevação frontal não há equivalente exato (ver nota abaixo) | O pré-projeto cita "elevação lateral de braço" e "abdução de ombro", que são o mesmo movimento; fica o nome "elevação lateral", mais fácil para o usuário. Trocar um deles pela elevação frontal dá 3 movimentos distintos, todos presentes nos datasets (UI-PRMD m01/m07/m10 e KIMORE Es5/Es1). |
| D2 | App roda localmente (Streamlit + OpenCV). Hugging Face Spaces vira opcional | Tomada | Pedido de simplicidade; webcam em Spaces exige WebRTC e é frágil para demo ao vivo. |
| D3 | Usuário escolhe o exercício na interface | Tomada | Reconhecimento automático do exercício não está nos objetivos e acrescenta um modelo a mais. Fica como PODE. |
| D4 | O app usa as **regras** (calibradas com webcam) para julgar as repetições; RF e LSTM ficam só no modo experimental | Tomada (24/11/2026) | Nos vídeos do grupo as regras acertaram 85–100% e o RF 0–30% (0% na elevação frontal); treinados com Kinect, os modelos não generalizam para câmera comum (cenários C, F e F2). O RF segue como melhor modelo nos dados de Kinect (cenário A) e entra na comparação do relatório. |
| D5 | MediaPipe é o estimador padrão; YOLO-pose é avaliado como alternativa | Tomada | Sugestão do professor. Ambos expõem as 12 articulações do subconjunto comum. |
| D6 | Ângulos calculados em 3D (world landmarks) quando o estimador oferecer, 2D caso contrário | Proposta — validar em [07](07-testes-robustez.md) | 3D aproxima mais do Kinect; YOLO-pose só dá 2D. |
| D7 | Rótulo binário do KIMORE por limiar na pontuação clínica do exercício | Limiar provisório 40/50 em `data/kimore.py`; confirmar pela distribuição das notas | KIMORE não tem rótulo correto/incorreto, só pontuação. |

**Nota sobre D1 (elevação frontal):** nenhum dataset tem exatamente o nosso movimento (braços pela frente até a altura dos ombros, ~90–110° medidos). O UI-PRMD m10 (escapção) sobe só até ~68° nas repetições corretas e o KIMORE Es1 eleva os braços acima da cabeça (~160°). O modelo da elevação frontal é treinado com os dois, então seu veredito é menos confiável que o dos outros exercícios; as regras de feedback (calibradas com webcam) seguem como referência principal para esse exercício.

## Glossário

- **Repetição (rep)**: um ciclo completo do movimento (ex.: descer e subir no agachamento).
- **Série**: sequência de repetições sem pausa longa (alvo: 10).
- **Ângulo principal**: o ângulo usado para contar repetições de cada exercício (ex.: joelho no agachamento).
- **Esqueleto comum**: as 12 articulações presentes em Kinect, MediaPipe e YOLO-pose (ombros, cotovelos, punhos, quadris, joelhos, tornozelos).
- **Participante não visto**: pessoa cujos dados não aparecem em nenhum momento no treino.

# Monitoramento Inteligente de Exercícios de Reabilitação Física por Visão Computacional

Sistema que, pela webcam de um computador comum, acompanha exercícios de fisioterapia domiciliar: **conta as repetições** e indica **em tempo real se cada repetição foi executada corretamente**.

> **Aviso:** esta ferramenta é um projeto acadêmico. Ela **não faz diagnóstico nem prescreve exercícios** e não substitui o fisioterapeuta. É um apoio à prática orientada por um profissional. Interrompa o exercício se sentir dor.

## Como funciona

```
Webcam ──► Estimativa de pose ──► Ângulos articulares ──┬──► Contagem de repetições
           (MediaPipe ou YOLO-pose)                     │
                                                        └──► Avaliação (regras calibradas)
                                                                  │ correta × incorreta
                                                                  ▼
                                                     Interface Streamlit com feedback ao vivo
```

1. **Estimativa de pose:** um modelo pré-treinado (MediaPipe BlazePose, com YOLO-pose como alternativa) encontra as articulações do corpo em cada quadro.
2. **Atributos:** as articulações viram ângulos (joelho, quadril, ombro, cotovelo, tronco), que não dependem da distância nem da posição da pessoa na imagem.
3. **Contagem:** detecção de picos e vales no ângulo principal de cada exercício, sem treino.
4. **Classificação:** cada repetição é julgada como correta ou incorreta por regras sobre os ângulos, calibradas com testes em webcam. Também treinamos e comparamos Random Forest e LSTM com datasets públicos: eles vão bem com dados de Kinect, mas não generalizam para câmera comum, por isso o app usa as regras (resultados em [reports/results.md](reports/results.md)).
5. **Feedback:** a interface mostra o contador, o veredito de cada repetição e dicas como "desça um pouco mais".

### Exercícios

| Exercício | Posição da câmera |
|---|---|
| Agachamento profundo | lateral |
| Elevação lateral de braço | frontal |
| Elevação frontal de braço | lateral |

## Metas

| Meta | Valor |
|---|---|
| F1 macro (correto × incorreto) em pessoas não vistas no treino | ≥ 0,80 |
| Erro na contagem de repetições | ≤ 1 por série de 10 |
| Desempenho em notebook sem GPU | ≥ 15 FPS |

Além disso, o sistema é avaliado sob diferentes condições de iluminação, câmera, distância, ângulo, fundo, roupa e oclusão.

## Dados

| Base | Uso no projeto |
|---|---|
| UI-PRMD (Vakanski et al., 2018) | Treino: esqueletos de Kinect com repetições corretas e incorretas |
| KIMORE (Capecci et al., 2019) | Treino e avaliação com pacientes reais; vídeos RGB para comparar Kinect × câmera comum |
| REHAB24-6 (Černek; Sedmidubský; Budíková, 2024) | Teste externo com vídeos RGB e rótulo por repetição (CC BY-NC 4.0) |
| Vídeos gravados pelo grupo | Teste em condições reais e testes de robustez |

Os dados brutos **não** são versionados neste repositório. Cada base deve ser baixada da fonte original, respeitando seus termos de uso.

## Tecnologias

Python 3.11 · MediaPipe · Ultralytics YOLO · OpenCV · scikit-learn · PyTorch · Streamlit · pytest · GitHub Actions

O Ultralytics YOLO é distribuído sob a licença AGPL-3.0.

## Como rodar

Requer apenas um computador com webcam; não precisa de GPU nem de internet depois da instalação.

1. Instale o [uv](https://docs.astral.sh/uv/getting-started/installation/) (ele baixa o Python 3.11 sozinho).
2. Instale as dependências e baixe os modelos de pose pré-treinados:

   ```bash
   uv sync
   uv run python -m reabvision.pose.download
   ```

3. Abra o app:

   ```bash
   uv run streamlit run src/reabvision/app/main.py
   ```

Alternativa sem Streamlit, em janela do OpenCV (teclas: `q` sai, `r` reinicia a série):

```bash
uv run python -m reabvision.app.cli --exercise squat
uv run python -m reabvision.app.cli --exercise lateral_raise --estimator yolo --source video.mp4
```

Testes: `uv run pytest`.

### Reproduzir os experimentos

Os dados não ficam no repositório. Para baixar, treinar e avaliar (tudo em CPU):

```bash
uv run python -m reabvision.data.download              # UI-PRMD, KIMORE e REHAB24-6 (~3,3 GB)
uv run python -m reabvision.data.rehab24                # extrai a pose dos vídeos do REHAB24-6
uv run python -m reabvision.models.train                # Random Forest e LSTM por exercício
uv run python -m reabvision.models.evaluate             # gera reports/results.md
uv run python -m reabvision.robustness.robustness       # gera reports/robustness_*.md
```

Vídeos próprios para avaliação vão em `data/own/videos/`, com as anotações em `data/own/annotations.csv` (formato em [specs/01-dados.md](specs/01-dados.md)).

Para calibrar limiares, defina `REABVISION_DEBUG_DIR=<pasta>` ao rodar o app: ele grava um log numérico (ângulos, contagem, dicas) de cada série, sem imagens.

## Privacidade

O vídeo da webcam é processado apenas localmente, quadro a quadro, e nunca é salvo nem enviado a servidores. Somente as coordenadas do esqueleto são usadas.

## Documentação

- [Apresentação](docs/apresentacao.html): síntese de tecnologias, testes e resultados (abrir no navegador)
- [Resultados da avaliação](reports/results.md)
- [Pré-projeto](docs/pre-projeto/pre-projeto-grupo5.pdf)
- [Especificações](specs/README.md)
- [Tarefas](todos/README.md)

## Grupo 5

Alessandro da Rosa · Carlos M. · Estevan Stolfo · Felipe W. · João M. · Pedro Scheurer · Pedro Dagneze · João Pedro Ferraresi · Vinicius Amaral

## Referências

- CAPECCI, M. et al. The KIMORE dataset: KInematic assessment of MOvement and clinical scores for remote monitoring of physical REhabilitation. *IEEE TNSRE*, v. 27, n. 7, p. 1436-1448, 2019.
- ČERNEK, A.; SEDMIDUBSKÝ, J.; BUDÍKOVÁ, P. REHAB24-6: Physical Therapy Dataset for Analyzing Pose Estimation Methods. *SISAP*, 2024.
- VAKANSKI, A. et al. A data set of human body movements for physical rehabilitation exercises. *Data*, v. 3, n. 1, p. 2, 2018.
- BAZAREVSKY, V. et al. BlazePose: on-device real-time body pose tracking. arXiv:2006.10204, 2020.
- LIAO, Y.; VAKANSKI, A.; XIAN, M. A deep learning framework for assessing physical rehabilitation exercises. *IEEE TNSRE*, v. 28, n. 2, p. 468-477, 2020.

Lista completa no [pré-projeto](docs/pre-projeto/pre-projeto-grupo5.pdf).

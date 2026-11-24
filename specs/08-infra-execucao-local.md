# 08 — Infraestrutura e execução local

Prioridade: qualquer integrante consegue clonar o repo e rodar o app em poucos comandos, no próprio notebook.

## Estrutura do repositório

```
.
├── README.md                  # como instalar, rodar, treinar; aviso de uso
├── pyproject.toml             # dependências e config de ferramentas
├── configs/
│   ├── exercises.yaml         # limiares de contagem e regras de feedback
│   └── conditions.yaml        # matriz de robustez
├── data/                      # fora do git
│   ├── raw/  processed/  own/
├── docs/
│   └── pre-projeto/           # PDF do pré-projeto e comentário do professor
├── specs/                     # estas especificações
├── models/                    # modelos treinados (pequenos, podem ir pro git ou release)
├── notebooks/                 # exploração e experimentos (Colab-friendly)
├── reports/                   # resultados gerados por script
├── src/reabvision/
│   ├── data/                  # loaders UI-PRMD, KIMORE, vídeos próprios
│   ├── pose/                  # PoseEstimator, MediaPipe, YOLO
│   ├── features/              # ângulos, atributos por rep, sequências
│   ├── counting/              # contador online e offline
│   ├── models/                # RF, LSTM, Classifier, train.py, evaluate.py
│   ├── robustness/            # robustness.py, benchmark de FPS
│   └── app/                   # Streamlit (main.py) e plano B (cli.py)
└── tests/
```

Nome do pacote (`reabvision`) é provisório.

## Ambiente

- Python 3.11 (MediaPipe ainda não acompanha sempre a versão mais nova do Python; fixar 3.11).
- Gerenciador: `uv` ou `pip` + `venv`. Documentar os dois no README.
- PyTorch versão CPU por padrão (instalação menor).
- Dependências principais: `mediapipe`, `opencv-python`, `ultralytics`, `numpy`, `pandas`, `scipy`, `scikit-learn`, `torch`, `streamlit`, `pyyaml`, `joblib`, `matplotlib`. Dev: `pytest`, `ruff`.

Comandos-alvo:

```bash
uv sync                               # ou: python -m venv .venv && pip install -e .[dev]
uv run streamlit run src/reabvision/app/main.py
uv run python -m reabvision.models.train --model rf --exercise squat
uv run python -m reabvision.models.evaluate
uv run pytest
```

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| INF-01 | Estrutura acima criada, com `.gitignore` cobrindo `data/`, `.venv/`, vídeos e cache | DEVE |
| INF-02 | README com instalação, execução do app, treino, avaliação e aviso de uso | DEVE |
| INF-03 | Modelos treinados disponíveis para o app sem precisar treinar (commit se < ~20 MB, senão GitHub Release) | DEVE |
| INF-04 | `pytest` cobrindo ângulos, mapeamento de articulações, contador, divisão por participante, loaders (com amostras pequenas versionadas em `tests/fixtures/`) | DEVE |
| INF-05 | GitHub Actions rodando `ruff` e `pytest` a cada push/PR | DEVE |
| INF-06 | Dockerfile para rodar o app (webcam via `--device /dev/video0` no Linux) | PODE |
| INF-07 | Publicação no Hugging Face Spaces (modo vídeo de arquivo) | PODE |
| INF-08 | Testado em pelo menos 2 notebooks diferentes do grupo (idealmente Windows e Linux) | DEVE |

## Critérios de aceite

- Clone limpo + comandos do README → app abre e funciona com webcam.
- CI verde na branch principal.

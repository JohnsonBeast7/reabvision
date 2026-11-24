# 08 — Infra e execução local

Spec: [08-infra-execucao-local.md](../specs/08-infra-execucao-local.md)

## Esqueleto (semana 1)

- [ ] Criar estrutura de pastas (`src/`, `tests/`, `configs/`, `notebooks/`, `reports/`, `models/`, `data/`) (INF-01)
- [ ] `.gitignore` cobrindo `data/`, `.venv/`, vídeos, caches (INF-01)
- [ ] `pyproject.toml` com Python 3.11 e dependências (PyTorch CPU)
- [ ] Testar instalação com `uv` e com `pip` + `venv`
- [ ] Configurar `ruff` e `pytest`
- [ ] README inicial com instalação e comandos (INF-02)

## Ao longo do projeto

- [ ] Fixtures pequenas de UI-PRMD e KIMORE em `tests/fixtures/` (INF-04)
- [ ] Cobertura de testes: ângulos, mapeamento, contador, divisão por participante, loaders (INF-04)
- [ ] GitHub Actions rodando `ruff` e `pytest` em push/PR (INF-05)
- [ ] Disponibilizar modelos treinados no repo ou em GitHub Release (INF-03)

## Antes da apresentação

- [ ] Clone limpo + README → app funcionando, em pelo menos 2 notebooks (Windows e Linux) (INF-08)
- [ ] README final: instalação, app, treino, avaliação, aviso de uso, citações dos datasets (INF-02)
- [ ] Dockerfile **(PODE)** (INF-06)
- [ ] Hugging Face Spaces em modo vídeo de arquivo **(PODE)** (INF-07)

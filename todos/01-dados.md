# 01 — Dados

Spec: [01-dados.md](../specs/01-dados.md)

## Obtenção

- [x] Baixar UI-PRMD (parte Kinect) e registrar origem e condições de uso (DAT-01)
- [x] Baixar KIMORE (Es1/Es5, posições e rótulos; cópia do Google Drive) e registrar origem e condições de uso (DAT-01)
- [x] Baixar `videos.zip` e `Segmentation.csv` do REHAB24-6 (Zenodo 13305826, CC BY-NC 4.0) e registrar citação (DAT-01)
- [x] Script `scripts/download_data` (ou instruções no README, se o download exigir cadastro) que organiza em `data/raw/<dataset>/` (DAT-01)
- [x] Garantir `data/` no `.gitignore` (DAT-02)

## Inspeção e decisões

- [x] Inspecionar formato dos arquivos de UI-PRMD (posições, ângulos, segmentação por repetição)
- [x] Inspecionar formato dos arquivos de KIMORE (posições, pontuações clínicas, grupos)
- [x] Inspecionar REHAB24-6: qual câmera usar, formato da segmentação e dos rótulos
- [x] Confirmar mapeamento dos exercícios: m01/m07/m10 (UI-PRMD) e Es5/Es1 (KIMORE) para `squat`, `lateral_raise`, `front_raise` (D1)
- [x] Verificar se m10 é próximo o suficiente da elevação frontal; se não, escolher substituto e atualizar spec 00 (D1) — m10 sobe só ~68° e é com um braço; mantido como aproximação (nota na spec 00)
- [x] Analisar distribuição das pontuações clínicas do KIMORE e definir limiar correto/incorreto (D7)
- [x] Registrar limiar escolhido em `configs/` e na spec 01 (D7)

## Código

- [x] Dataclass `Sequence` e ordem fixa das 12 articulações
- [x] Mapeamento Kinect v1/v2 → esqueleto comum, com teste (DAT-06)
- [x] Reamostragem temporal para 30 Hz, com teste (DAT-09)
- [x] Loader UI-PRMD → `Sequence`, com teste em fixture pequena (DAT-03)
- [x] Loader KIMORE → `Sequence` com pontuação e grupo clínico, com teste em fixture pequena (DAT-04)
- [x] Extrator de vídeos próprios: roda estimador de pose e salva `Sequence`, sem salvar quadros (DAT-05) — own_eval / robustness (pose em memória, sem salvar quadros)
- [x] Salvar sequências processadas em `data/processed/` — data/processed/rehab24/
- [x] Criar `data/own/annotations.csv` com o esquema da spec (DAT-07)
- [x] Loader REHAB24-6: pose sobre o RGB, rótulo por repetição, só `squat` e `lateral_raise` (DAT-10)

## Análise

- [ ] Notebook exploratório: amostras por exercício, rótulo, participante e grupo (DAT-08)

# 01 — Dados

Spec: [01-dados.md](../specs/01-dados.md)

## Obtenção

- [ ] Baixar UI-PRMD (parte Kinect) e registrar origem e condições de uso (DAT-01)
- [ ] Baixar KIMORE (incluindo vídeos RGB) e registrar origem e condições de uso (DAT-01)
- [ ] Baixar `videos.zip` e `Segmentation.csv` do REHAB24-6 (Zenodo 13305826, CC BY-NC 4.0) e registrar citação (DAT-01)
- [ ] Script `scripts/download_data` (ou instruções no README, se o download exigir cadastro) que organiza em `data/raw/<dataset>/` (DAT-01)
- [ ] Garantir `data/` no `.gitignore` (DAT-02)

## Inspeção e decisões

- [ ] Inspecionar formato dos arquivos de UI-PRMD (posições, ângulos, segmentação por repetição)
- [ ] Inspecionar formato dos arquivos de KIMORE (posições, pontuações clínicas, grupos, vídeos RGB)
- [ ] Inspecionar REHAB24-6: qual câmera usar, formato da segmentação e dos rótulos
- [ ] Confirmar mapeamento dos exercícios: m01/m07/m10 (UI-PRMD) e Es5/Es1 (KIMORE) para `squat`, `lateral_raise`, `front_raise` (D1)
- [ ] Verificar se m10 é próximo o suficiente da elevação frontal; se não, escolher substituto e atualizar spec 00 (D1)
- [ ] Analisar distribuição das pontuações clínicas do KIMORE e definir limiar correto/incorreto (D7)
- [ ] Registrar limiar escolhido em `configs/` e na spec 01 (D7)

## Código

- [ ] Dataclass `Sequence` e ordem fixa das 12 articulações
- [ ] Mapeamento Kinect v1/v2 → esqueleto comum, com teste (DAT-06)
- [ ] Reamostragem temporal para 30 Hz, com teste (DAT-09)
- [ ] Loader UI-PRMD → `Sequence`, com teste em fixture pequena (DAT-03)
- [ ] Loader KIMORE → `Sequence` com pontuação e grupo clínico, com teste em fixture pequena (DAT-04)
- [ ] Extrator de vídeos próprios: roda estimador de pose e salva `Sequence`, sem salvar quadros (DAT-05)
- [ ] Salvar sequências processadas em `data/processed/`
- [ ] Criar `data/own/annotations.csv` com o esquema da spec (DAT-07)
- [ ] Loader REHAB24-6: pose sobre o RGB, rótulo por repetição, só `squat` e `lateral_raise` (DAT-10)
- [ ] Extrair pose (MediaPipe e YOLO) do RGB do KIMORE, pareada com o esqueleto Kinect (DAT-11)

## Análise

- [ ] Notebook exploratório: amostras por exercício, rótulo, participante e grupo (DAT-08)

# 07 — Testes de robustez

Spec: [07-testes-robustez.md](../specs/07-testes-robustez.md)

## Preparação

- [ ] Criar `configs/conditions.yaml` com a matriz C00–C17 (ROB-01)
- [ ] Imprimir lista de checagem para as sessões de gravação
- [ ] Planejar escala: quem grava quais condições e exercícios (12 condições obrigatórias × 2 pessoas × 3 exercícios = 72 séries)
- [ ] Confirmar termos de consentimento assinados antes de gravar (ETI-04)

## Gravação (3 exercícios, ≥ 2 integrantes por condição, séries de 10 com algumas reps incorretas)

- [ ] C00 Base, com o máximo de integrantes possível
- [ ] C01 Pouca luz
- [ ] C02 Contraluz
- [ ] C04 Resolução 480p
- [ ] C05 Celular como câmera
- [ ] C07 Perto (~1,5 m)
- [ ] C08 Longe (~4 m)
- [ ] C09 Câmera a 45°
- [ ] C12 Fundo poluído
- [ ] C13 Outra pessoa ao fundo
- [ ] C14 Roupa larga
- [ ] C15 Oclusão parcial
- [ ] C03 Luz lateral forte **(PODE)** (ROB-03)
- [ ] C06 Webcam USB externa **(PODE)** (ROB-03)
- [ ] C10 Vista trocada **(PODE)** (ROB-03)
- [ ] C11 Altura da câmera **(PODE)** (ROB-03)
- [ ] C16 Execução rápida **(PODE)** (ROB-03)
- [ ] C17 Execução lenta **(PODE)** (ROB-03)
- [ ] Anotar cada vídeo em `annotations.csv` logo após gravar (DAT-07)

## Análise

- [ ] Script `robustness.py`: roda MediaPipe e YOLO-pose em todos os vídeos (ROB-04)
- [ ] Métricas por condição: taxa de detecção, estabilidade, erro de contagem, F1 macro, FPS (ROB-04)
- [ ] Gráfico de queda relativa à condição base (ROB-04)
- [ ] Seção no relatório: condições que mais degradam e recomendações de uso (ROB-05)
- [ ] Degradações sintéticas (escurecer, ruído, blur, resolução) **(PODE)** (ROB-06)

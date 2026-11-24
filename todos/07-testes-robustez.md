# 07 — Testes de robustez

Spec: [07-testes-robustez.md](../specs/07-testes-robustez.md)

## Preparação

- [ ] Criar `configs/conditions.yaml` com a matriz de condições e a fonte de cada uma (ROB-01)
- [ ] Mandar ao grupo o plano de gravação (27 vídeos, 5 pessoas) e definir quem é A, B, C, D e E
- [ ] Confirmar termos de consentimento assinados antes de gravar (ETI-04)

## Gravação própria (3 exercícios por condição, séries de 10 com ~3 reps incorretas anotadas)

- [ ] C00 Base: pessoas A, B, C, D e E (15 vídeos)
- [ ] C05 Celular como câmera: pessoa A (3 vídeos)
- [ ] C08 Longe (~4 m): pessoa B (3 vídeos)
- [ ] C14 Roupa larga: pessoa C (3 vídeos)
- [ ] C15 Objeto cobrindo parte das pernas: pessoa D (3 vídeos)
- [ ] Anotar cada vídeo em `annotations.csv` logo após gravar (DAT-07)
- [ ] Condições não cobertas (C02, C03, C06, C07, C12) **(PODE)** (ROB-03)

## Análise

- [ ] Script `robustness.py`: roda MediaPipe e YOLO-pose nos vídeos próprios, no REHAB24-6 (por metadado de condição) e nas versões sintéticas (ROB-04)
- [ ] Métricas por condição: taxa de detecção, estabilidade, erro de contagem, F1 macro, FPS (ROB-04)
- [ ] Gráfico de queda relativa à condição base (ROB-04)
- [ ] Seção no relatório: condições que mais degradam e recomendações de uso (ROB-05)
- [ ] Degradações sintéticas (escurecer, resolução, ruído, desfoque) em níveis crescentes (ROB-06)

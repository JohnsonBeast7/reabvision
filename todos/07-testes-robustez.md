# 07 — Testes de robustez

Spec: [07-testes-robustez.md](../specs/07-testes-robustez.md)

## Preparação

- [ ] Criar `configs/conditions.yaml` com a matriz de condições e a fonte de cada uma (ROB-01)
- [x] Mandar ao grupo o plano de gravação

## Gravação própria (3 exercícios por condição, séries de 10 com ~3 reps incorretas anotadas)

- [x] Gravação encerrada com 9 vídeos de 4 pessoas (celular, C05; alguns com vista trocada, C10)
- [x] C08 Longe: simulada por degradação sintética (sem vídeo próprio)
- [ ] C14 Roupa larga: não gravada — registrar como limitação no relatório
- [ ] C15 Oclusão: não gravada — registrar como limitação no relatório
- [x] Anotar os vídeos em `annotations.csv` (feito por inspeção visual; revisar com quem gravou) (DAT-07)
- [ ] Condições não cobertas (C02, C03, C06, C07, C12) **(PODE)** (ROB-03)

## Análise

- [x] Script `robustness.py`: roda MediaPipe e YOLO-pose nos vídeos próprios, no REHAB24-6 (por metadado de condição) e nas versões sintéticas (ROB-04)
- [ ] Métricas por condição: taxa de detecção, estabilidade, erro de contagem, F1 macro, FPS (ROB-04)
- [ ] Gráfico de queda relativa à condição base (ROB-04)
- [ ] Seção no relatório: condições que mais degradam e recomendações de uso (ROB-05)
- [x] Degradações sintéticas (escurecer, resolução, ruído, desfoque) em níveis crescentes (ROB-06)

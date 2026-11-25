# 03 — Contagem de repetições

Spec: [03-contagem-repeticoes.md](../specs/03-contagem-repeticoes.md)

- [x] Criar `configs/exercises.yaml` com direção, limiares de histerese, durações e amplitude mínima por exercício (REP-01)
- [x] Contador online (máquina de estados) emitindo eventos `Rep` (REP-01)
- [x] Interpolação de falhas curtas (≤ 0,3 s) e pausa da contagem em falhas longas
- [x] Segmentador offline com `scipy.signal.find_peaks` usando os mesmos parâmetros (REP-02)
- [x] Testes sintéticos: 10 ciclos → 10 reps, ruído, pausa no meio, repetição parcial não conta (REP-03)
- [x] Teste de concordância entre contador online e offline
- [x] Segmentar séries do KIMORE em repetições com o segmentador offline
- [ ] Ajustar limiares com vídeos de 2 integrantes (REP-05)
- [x] Calibração inicial dos limiares com testes reais na webcam (1 pessoa, 3 exercícios) — log de depuração em `REABVISION_DEBUG_DIR`
- [x] Script de erro absoluto médio da contagem nos vídeos dos demais integrantes (REP-04)
- [x] Verificar META-02 (≤ 1 rep de erro por série de 10) — média 0,8–1,0 nos vídeos próprios (máx 2)

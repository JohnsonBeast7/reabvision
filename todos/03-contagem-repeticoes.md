# 03 — Contagem de repetições

Spec: [03-contagem-repeticoes.md](../specs/03-contagem-repeticoes.md)

- [ ] Criar `configs/exercises.yaml` com direção, limiares de histerese, durações e amplitude mínima por exercício (REP-01)
- [ ] Contador online (máquina de estados) emitindo eventos `Rep` (REP-01)
- [ ] Interpolação de falhas curtas (≤ 0,3 s) e pausa da contagem em falhas longas
- [ ] Segmentador offline com `scipy.signal.find_peaks` usando os mesmos parâmetros (REP-02)
- [ ] Testes sintéticos: 10 ciclos → 10 reps, ruído, pausa no meio, repetição parcial não conta (REP-03)
- [ ] Teste de concordância entre contador online e offline
- [ ] Segmentar séries do KIMORE em repetições com o segmentador offline
- [ ] Ajustar limiares com vídeos de 2 integrantes (REP-05)
- [ ] Script de erro absoluto médio da contagem nos vídeos dos demais integrantes (REP-04)
- [ ] Verificar META-02 (≤ 1 rep de erro por série de 10)

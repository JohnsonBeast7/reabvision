# 05 — Avaliação

Spec: [05-avaliacao.md](../specs/05-avaliacao.md)

- [ ] Funções de divisão por participante (LOSO/`GroupKFold` no UI-PRMD, `GroupShuffleSplit` estratificado no KIMORE) (AVA-01)
- [ ] Teste: interseção vazia de `subject_id` entre treino e teste (AVA-01)
- [ ] Script `evaluate.py` gerando `reports/results.md` e figuras (AVA-02)
- [ ] Cenário A: UI-PRMD → UI-PRMD não vistos
- [ ] Cenário B: UI-PRMD + KIMORE → KIMORE não vistos, saudáveis × pacientes
- [ ] Cenário C: UI-PRMD + KIMORE → vídeos próprios (webcam)
- [ ] Cenário D: cenário C com YOLO-pose no lugar do MediaPipe
- [ ] Matrizes de confusão por modelo e exercício
- [ ] Benchmark de FPS (média e percentil 5 em 60 s) em pelo menos 2 notebooks sem GPU (AVA-03)
- [ ] Conferir metas META-01 a META-04 e explicar as não atingidas
- [ ] Relatório: RF × LSTM, viés, Kinect × webcam, MediaPipe × YOLO, limitações (AVA-04)
- [ ] Análise de erros com exemplos de repetições mal classificadas **(PODE)** (AVA-05)

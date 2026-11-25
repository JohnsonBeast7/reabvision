# 05 — Avaliação

Spec: [05-avaliacao.md](../specs/05-avaliacao.md)

- [x] Funções de divisão por participante (LOSO/`GroupKFold` no UI-PRMD, `GroupShuffleSplit` estratificado no KIMORE) (AVA-01)
- [ ] Teste: interseção vazia de `subject_id` entre treino e teste (AVA-01)
- [x] Script `evaluate.py` gerando `reports/results.md` e figuras (AVA-02)
- [x] Cenário A: UI-PRMD → UI-PRMD não vistos
- [x] Cenário B: UI-PRMD + KIMORE → KIMORE não vistos, saudáveis × pacientes
- [x] Cenário C: UI-PRMD + KIMORE → vídeos próprios (webcam)
- [x] Cenário D: cenário C com YOLO-pose no lugar do MediaPipe
- [x] Cenário F: REHAB24-6 (`squat` e `lateral_raise`), treino só com Kinect
- [x] Cenário F2: treino com Kinect + REHAB24-6, cada pessoa do REHAB24-6 fora do treino
- [ ] Cenário B com várias divisões (média ± desvio)
- [ ] Erro de contagem também no REHAB24-6
- [ ] Matrizes de confusão por modelo e exercício
- [ ] Benchmark de FPS (média e percentil 5 em 60 s) em pelo menos 2 notebooks sem GPU (AVA-03)
- [ ] Conferir metas META-01 a META-04 e explicar as não atingidas
- [ ] Relatório: RF × LSTM, viés, Kinect × webcam, MediaPipe × YOLO, limitações (AVA-04)
- [ ] Análise de erros com exemplos de repetições mal classificadas **(PODE)** (AVA-05)

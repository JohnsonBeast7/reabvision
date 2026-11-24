# 03 — Contagem de repetições

Método determinístico, sem treino: detecção de picos e vales no sinal do ângulo principal do exercício ([02](02-pose-e-features.md#ângulo-principal-por-exercício-usado-na-contagem)).

## Algoritmo

1. Sinal de entrada: ângulo principal por quadro, já suavizado; quadros inválidos interpolados se a falha for curta (≤ 0,3 s), senão a contagem pausa.
2. Cada exercício define, em `configs/exercises.yaml`:
   - direção do movimento (o ângulo **diminui** no agachamento, **aumenta** nas elevações de braço);
   - `rest_threshold` e `active_threshold` (histerese) em graus;
   - `min_rep_duration` e `max_rep_duration` em segundos;
   - `min_amplitude` em graus.
3. Máquina de estados com histerese: `REPOUSO → MOVIMENTO → PICO → RETORNO → REPOUSO`. Uma repetição é contada ao voltar ao repouso se amplitude e duração estão dentro dos limites.
4. Cada repetição contada emite um evento `Rep(start_frame, peak_frame, end_frame, amplitude)`, que é a janela entregue ao classificador.

Versão offline (para avaliar e para extrair repetições dos datasets): `scipy.signal.find_peaks` com `prominence` e `distance` derivados dos mesmos parâmetros. A versão online (máquina de estados) e a offline DEVEM concordar nos vídeos de teste.

## Segmentação dos datasets

- UI-PRMD já vem segmentado por repetição → usar direto.
- KIMORE vem como série contínua → segmentar com a versão offline; repetições herdam o rótulo da série (D7).
- Vídeos próprios → segmentar com a versão offline e comparar com `n_reps_real` da anotação.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| REP-01 | Contador online (máquina de estados) com parâmetros por exercício em YAML | DEVE |
| REP-02 | Segmentador offline (`find_peaks`) com os mesmos parâmetros | DEVE |
| REP-03 | Testes com sinais sintéticos: senoide com 10 ciclos → 10 reps; ruído; pausa no meio; repetição parcial (amplitude curta) não conta | DEVE |
| REP-04 | Script que calcula o erro absoluto médio da contagem nos vídeos próprios | DEVE |
| REP-05 | Ajuste dos limiares feito só com parte dos vídeos próprios (ex.: de 2 integrantes) e avaliado nos demais | DEVE |

## Critérios de aceite

- Erro absoluto médio ≤ 1 repetição por série de 10 nos vídeos próprios em condição base (META-02).
- Todos os testes de REP-03 passam.

# 06 — Aplicação

Spec: [06-aplicacao.md](../specs/06-aplicacao.md)

## Base

- [ ] Tela de aviso de uso com botão "Entendi" antes de abrir a câmera (ETI-02)
- [ ] Captura da webcam com OpenCV em laço + `st.image` (APP-01)
- [ ] Desenho do esqueleto sobre o vídeo (APP-01)
- [ ] Interface toda em português (APP-12)
- [ ] Garantir que nenhum quadro é salvo nem enviado (APP-11)

## Exercício

- [ ] Seleção de exercício: agachamento / elevação lateral / elevação frontal (APP-02)
- [ ] Texto e imagem de referência da posição da câmera por exercício (APP-02)
- [ ] Contador de repetições ao vivo (APP-03)
- [ ] Veredito por repetição com cor e confiança (APP-04)
- [ ] Dicas das regras de feedback (APP-05)
- [ ] Aviso de pose inválida (corpo não detectado / afaste-se / iluminação) (APP-06)
- [ ] FPS no canto da tela
- [ ] Resumo ao parar: total, corretas, dicas frequentes (APP-07)
- [ ] Botão reiniciar

## Barra lateral

- [ ] Escolha de câmera e resolução
- [ ] Troca de estimador MediaPipe / YOLO-pose (APP-08)
- [ ] Troca de modelo RF / LSTM (APP-08)
- [ ] Modo vídeo de arquivo (APP-09)

## Extras

- [ ] Plano B com janela `cv2.imshow` **(PODE)** (APP-10)
- [ ] Reconhecimento automático do exercício **(PODE)** (APP-13)

## Validação

- [ ] Medir FPS do app com MediaPipe (≥ 15) em notebook sem GPU
- [ ] Teste manual: 10 agachamentos → contador 10 ± 1
- [ ] Atualizar instruções de posicionamento com os resultados da robustez (ROB-05)

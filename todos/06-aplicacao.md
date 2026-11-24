# 06 — Aplicação

Spec: [06-aplicacao.md](../specs/06-aplicacao.md)

## Base

- [x] Tela de aviso de uso com botão "Entendi" antes de abrir a câmera (ETI-02)
- [x] Captura da webcam com OpenCV em laço + `st.image` (APP-01)
- [x] Desenho do esqueleto sobre o vídeo (APP-01)
- [x] Interface toda em português (APP-12)
- [x] Garantir que nenhum quadro é salvo nem enviado (APP-11)

## Exercício

- [x] Seleção de exercício: agachamento / elevação lateral / elevação frontal (APP-02)
- [ ] Texto e imagem de referência da posição da câmera por exercício (APP-02)
- [x] Contador de repetições ao vivo (APP-03)
- [x] Veredito por repetição com cor e confiança (APP-04)
- [x] Dicas das regras de feedback (APP-05)
- [x] Aviso de pose inválida (corpo não detectado / afaste-se / iluminação) (APP-06)
- [x] FPS no canto da tela
- [x] Resumo ao parar: total, corretas, dicas frequentes (APP-07)
- [x] Botão reiniciar

## Barra lateral

- [x] Escolha de câmera e resolução
- [x] Troca de estimador MediaPipe / YOLO-pose (APP-08)
- [x] Troca de modelo RF / LSTM (APP-08)
- [x] Modo vídeo de arquivo (APP-09)

## Extras

- [x] Plano B com janela `cv2.imshow` **(PODE)** (APP-10)
- [ ] Reconhecimento automático do exercício **(PODE)** (APP-13)

## Validação

- [x] Medir FPS do app com MediaPipe (≥ 15) em notebook sem GPU — 30 FPS na webcam
- [x] Teste manual: 10 agachamentos → contador 10 ± 1 — 10/10, e 10/10 e 9/9 nas elevações
- [ ] Atualizar instruções de posicionamento com os resultados da robustez (ROB-05)

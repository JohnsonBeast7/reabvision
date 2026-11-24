# 06 — Aplicação (demonstração local)

App simples, roda no notebook do apresentador, sem internet e sem GPU.

## Stack

- **Streamlit** para a interface.
- **OpenCV** (`cv2.VideoCapture`) para capturar a webcam num laço, atualizando um `st.image` a cada quadro. Funciona bem localmente e evita a complexidade de WebRTC (D2).
- Plano B para a apresentação: script `python -m <pacote>.app.cli` que abre uma janela `cv2.imshow` com o mesmo overlay, caso o Streamlit dê problema.

## Fluxo do usuário

1. Abre o app (`streamlit run app/main.py`). Aparece o aviso de uso ([09](09-etica-privacidade.md)) e um botão "Entendi".
2. Escolhe o exercício (agachamento / elevação lateral de braço / elevação frontal de braço) e vê um texto curto + imagem de referência da posição da câmera (frontal ou lateral, distância recomendada).
3. Clica em **Iniciar**. O vídeo aparece com o esqueleto desenhado.
4. Durante a série, a tela mostra:
   - contador de repetições;
   - veredito da última repetição (verde "Correta" / vermelho "Incorreta") com a confiança;
   - dica da regra de feedback, quando houver;
   - aviso de "corpo não detectado / afaste-se da câmera / melhore a iluminação" quando a pose estiver inválida;
   - FPS atual (pequeno, no canto — útil na demonstração).
5. Clica em **Parar**. Aparece o resumo: total de reps, quantas corretas, dicas mais frequentes.
6. Botão **Reiniciar** zera a sessão.

## Opções na barra lateral

- Câmera (índice 0, 1, …) e resolução (480p / 720p).
- Estimador de pose: MediaPipe (padrão) / YOLO-pose.
- Modelo: RF (padrão) / LSTM.
- Modo **vídeo de arquivo**: processar um vídeo gravado em vez da webcam (garante a demo se a webcam ou a iluminação da sala falharem).

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| APP-01 | Captura de webcam e exibição com esqueleto desenhado | DEVE |
| APP-02 | Seleção de exercício e instruções de posicionamento | DEVE |
| APP-03 | Contador de repetições ao vivo | DEVE |
| APP-04 | Veredito por repetição usando `Classifier` ([04](04-modelos.md)) | DEVE |
| APP-05 | Dicas das regras de feedback | DEVE |
| APP-06 | Aviso de pose inválida | DEVE |
| APP-07 | Resumo da série ao parar | DEVE |
| APP-08 | Troca de estimador e de modelo pela barra lateral | DEVE |
| APP-09 | Modo vídeo de arquivo | DEVE |
| APP-10 | Plano B com janela OpenCV | PODE |
| APP-11 | Nenhum quadro é salvo em disco nem enviado pela rede | DEVE |
| APP-12 | Interface em português | DEVE |
| APP-13 | Reconhecimento automático do exercício (D3) | PODE |

## Critérios de aceite

- Em notebook sem GPU, o app roda a ≥ 15 FPS com MediaPipe na resolução padrão.
- Um integrante consegue fazer uma série de 10 agachamentos na frente da câmera e o contador termina em 10 ± 1.
- Ensaio completo da demonstração feito pelo menos uma vez na sala ou ambiente parecido, inclusive o plano B.

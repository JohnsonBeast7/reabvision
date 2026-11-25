# 10 — Documentação e apresentação

Sem spec própria: cobre as etapas "Documentação", "Preparação da apresentação" e "Apresentação" do cronograma do pré-projeto.

## Documentação

- [ ] Relatório final consolidando `reports/results.md` e a análise de robustez (AVA-04, ROB-05)
- [ ] Seção de limitações: viés, Kinect × webcam, condições que degradam
- [ ] **Destacar que o Random Forest acertou pouco nos vídeos de câmera comum** (0–30% nos vídeos do grupo; 0% na elevação frontal; F1 0,31–0,40 no REHAB24-6 treinando só com Kinect), apesar de bater a meta no Kinect (cenário A: 0,83–0,90). Por isso o app usa as regras (D4)
- [ ] Limitações não testadas: roupa larga (C14) e oclusão (C15); agachamento com só 1 vídeo próprio; rótulos dos vídeos próprios anotados por inspeção visual
- [ ] Atualizar as specs com as decisões tomadas durante o projeto (D1, D6, D7)
- [ ] Revisar README final (INF-02)

## Apresentação

- [ ] Slides: problema, arquitetura, dados, modelos (RF × LSTM), YOLO × MediaPipe, robustez, resultados × metas, ética
- [ ] Roteiro da demonstração ao vivo: quem executa os exercícios, posição da câmera, iluminação da sala
- [ ] Gravar vídeos de backup para o modo vídeo de arquivo (APP-09)
- [ ] Testar o app na sala ou em ambiente parecido, incluindo o plano B
- [ ] Ensaio completo cronometrado
- [ ] Separar respostas para perguntas prováveis: por que RF e não só LSTM, por que não YOLO como padrão (ou por que sim), como lidam com privacidade

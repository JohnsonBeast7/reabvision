# Comentário do professor sobre o pré-projeto

> Gostei bastante da ideia. Vai ser bacana demonstrarmos isso em sala de aula no dia da apresentação. Vai ser fundamental os testes que vocês mencionaram e também variar condições de iluminação, câmera e outras coisas que possam atrapalhar o modelo e deve ser especificadas. Só fiquei pensando se LSTM é de fato o melhor modelo para isso. A solução é testar. Random Forest é uma boa, porque performa bem. Sugiro pesquisar o modelo de detecção de objetos YOLO

## Como cada ponto foi tratado nas specs

| Ponto do professor | Onde é tratado |
|---|---|
| Demonstração em sala | [`specs/06-aplicacao.md`](../../specs/06-aplicacao.md), [`specs/08-infra-execucao-local.md`](../../specs/08-infra-execucao-local.md) |
| Testes de robustez (iluminação, câmera, etc.) especificados | [`specs/07-testes-robustez.md`](../../specs/07-testes-robustez.md) |
| LSTM é o melhor modelo? Testar | [`specs/04-modelos.md`](../../specs/04-modelos.md) (comparação RF × LSTM × alternativa leve) |
| Random Forest performa bem | [`specs/04-modelos.md`](../../specs/04-modelos.md) (RF é o modelo padrão do app) |
| Pesquisar YOLO | [`specs/02-pose-e-features.md`](../../specs/02-pose-e-features.md) (YOLO-pose como estimador alternativo) e [`specs/07-testes-robustez.md`](../../specs/07-testes-robustez.md) (comparação MediaPipe × YOLO) |

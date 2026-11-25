# 02 — Pose e atributos

Spec: [02-pose-e-features.md](../specs/02-pose-e-features.md)

## Estimadores de pose

- [x] Estudar YOLO-pose (Ultralytics): instalação, saída de 17 pontos, FPS em CPU (D5)
- [x] Interface `PoseEstimator` e dataclass `PoseResult` (POS-01)
- [x] Implementação MediaPipe usando `pose_world_landmarks`, variante lite/full configurável (POS-01)
- [x] Implementação YOLO-pose (modelo nano) atrás da mesma interface (POS-02)
- [x] Mapeamento MediaPipe (33 pontos) e COCO (17 pontos) → esqueleto comum (POS-03)
- [x] Teste de lado esquerdo × direito e espelhamento da webcam (POS-03)
- [x] Suavização temporal configurável (média móvel ou One-Euro) (POS-04)
- [x] Marcar quadros inválidos por visibilidade < 0,5 (POS-05)
- [x] Registrar licença AGPL-3.0 do Ultralytics no README

## Atributos

- [x] `compute_angles(joints)` com a lista fixa de ângulos (FEA-01)
- [x] Testes de ângulo com poses sintéticas (90°, 180°, tolerância 1°) (FEA-01)
- [x] Ângulo de inclinação do tronco (FEA-01)
- [x] Ângulo principal por exercício (`squat`, `lateral_raise`, `front_raise`)
- [x] Atributos por repetição para o RF: mín, máx, amplitude, média, desvio, velocidades, duração, assimetria (FEA-02)
- [x] Sequência por repetição reamostrada para 64 quadros + z-score com estatísticas do treino (FEA-03)
- [x] Garantir que treino e app importam o mesmo módulo de atributos (FEA-04)
- [ ] Valgo do joelho no plano frontal **(PODE)**

## Comparação

- [ ] Gráfico das distribuições de ângulos Kinect × MediaPipe × YOLO por exercício (FEA-05)
- [ ] Decidir ângulos 3D × 2D com base no gráfico e nos testes de robustez (D6)

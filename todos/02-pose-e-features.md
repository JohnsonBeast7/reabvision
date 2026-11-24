# 02 — Pose e atributos

Spec: [02-pose-e-features.md](../specs/02-pose-e-features.md)

## Estimadores de pose

- [ ] Interface `PoseEstimator` e dataclass `PoseResult` (POS-01)
- [ ] Implementação MediaPipe usando `pose_world_landmarks`, `model_complexity` configurável (POS-01)
- [ ] Implementação YOLO-pose (modelo nano) atrás da mesma interface (POS-02)
- [ ] Mapeamento MediaPipe (33 pontos) e COCO (17 pontos) → esqueleto comum (POS-03)
- [ ] Teste de lado esquerdo × direito e espelhamento da webcam (POS-03)
- [ ] Suavização temporal configurável (média móvel ou One-Euro) (POS-04)
- [ ] Marcar quadros inválidos por visibilidade < 0,5 (POS-05)
- [ ] Registrar licença AGPL-3.0 do Ultralytics no README

## Atributos

- [ ] `compute_angles(joints)` com a lista fixa de ângulos (FEA-01)
- [ ] Testes de ângulo com poses sintéticas (90°, 180°, tolerância 1°) (FEA-01)
- [ ] Ângulo de inclinação do tronco (FEA-01)
- [ ] Ângulo principal por exercício (`squat`, `lateral_raise`, `front_raise`)
- [ ] Atributos por repetição para o RF: mín, máx, amplitude, média, desvio, velocidades, duração, assimetria (FEA-02)
- [ ] Sequência por repetição reamostrada para 64 quadros + z-score com estatísticas do treino (FEA-03)
- [ ] Garantir que treino e app importam o mesmo módulo de atributos (FEA-04)
- [ ] Valgo do joelho no plano frontal **(PODE)**

## Comparação

- [ ] Gráfico das distribuições de ângulos Kinect × MediaPipe × YOLO por exercício (FEA-05)
- [ ] Decidir ângulos 3D × 2D com base no gráfico e nos testes de robustez (D6)

"""Plano B da demonstração (APP-10): janela OpenCV, sem Streamlit. Também mede FPS.

    uv run python -m reabvision.app.cli --exercise squat
    uv run python -m reabvision.app.cli --exercise lateral_raise --source video.mp4 --estimator yolo

Teclas: q = sair, r = reiniciar a série.
"""

from __future__ import annotations

import argparse

import cv2

from reabvision.app.draw import GREEN, RED, YELLOW, draw_skeleton, put_text
from reabvision.config import EXERCISES, load_exercises
from reabvision.models.classifier import load_classifier
from reabvision.pose import ESTIMATORS, make_estimator
from reabvision.session import ExerciseSession


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--exercise", choices=EXERCISES, default="squat")
    parser.add_argument("--estimator", choices=list(ESTIMATORS), default="mediapipe")
    parser.add_argument("--model", choices=["regras", "rf", "lstm"], default="regras")
    parser.add_argument("--source", default="0", help="índice da câmera ou caminho de vídeo")
    parser.add_argument("--no-mirror", action="store_true")
    parser.add_argument("--headless", action="store_true", help="sem janela (benchmark de FPS)")
    args = parser.parse_args()

    cfg = load_exercises()[args.exercise]
    classifier = None if args.model == "regras" else load_classifier(args.exercise, args.model)
    is_cam = args.source.isdigit()
    cap = cv2.VideoCapture(int(args.source) if is_cam else args.source)
    if not cap.isOpened():
        raise SystemExit(f"não foi possível abrir a fonte {args.source}")
    file_fps = None if is_cam else (cap.get(cv2.CAP_PROP_FPS) or 30.0)
    mirror = is_cam and not args.no_mirror

    def new_session() -> ExerciseSession:
        return ExerciseSession(cfg, make_estimator(args.estimator), classifier)

    session = new_session()
    fps_samples: list[float] = []
    frame_idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            state = session.process(frame, frame_idx / file_fps if file_fps else None)
            frame_idx += 1
            if state.fps:
                fps_samples.append(state.fps)
            if args.headless:
                continue

            draw_skeleton(frame, state.pose, state.valid)
            if mirror:
                frame = cv2.flip(frame, 1)
            put_text(frame, f"{cfg.name}  |  Repeticoes: {state.count}", (15, 35), scale=0.9)
            last = session.reps[-1] if session.reps else None
            y = 70
            if last is not None:
                if not last.counted:
                    put_text(frame, "Nao contada", (15, y), YELLOW)
                else:
                    label = "CORRETA" if last.correct else "INCORRETA"
                    put_text(
                        frame, f"Rep {last.index}: {label}", (15, y), GREEN if last.correct else RED
                    )
                for hint in last.hints:
                    y += 30
                    put_text(frame, f"- {hint}", (15, y), scale=0.6)
            if state.message:
                put_text(frame, state.message, (15, frame.shape[0] - 45), YELLOW, 0.6)
            put_text(frame, f"{state.fps:.1f} FPS", (15, frame.shape[0] - 15), scale=0.6)
            cv2.imshow("Monitor de Reabilitacao", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                session.close()
                session = new_session()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        session.close()

    s = session.summary()
    print(
        f"Repetições: {s.total} (corretas {s.correct}, incorretas {s.incorrect}, "
        f"não contadas {s.not_counted})"
    )
    if fps_samples:
        fps_sorted = sorted(fps_samples)
        p5 = fps_sorted[int(0.05 * (len(fps_sorted) - 1))]
        print(f"FPS médio: {sum(fps_samples) / len(fps_samples):.1f} | percentil 5: {p5:.1f}")


if __name__ == "__main__":
    main()

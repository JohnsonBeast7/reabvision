"""App Streamlit (spec 06). Rode com:

    uv run streamlit run src/reabvision/app/main.py

Fluxo: aviso de uso -> escolha do exercício -> preparação -> série ao vivo -> resumo.
"""

from __future__ import annotations

import html
import os
import tempfile
import time

import cv2
import streamlit as st

from reabvision.app.cameras import list_cameras
from reabvision.app.draw import draw_skeleton
from reabvision.config import EXERCISES, load_exercises
from reabvision.debug_log import logger_from_env
from reabvision.models.classifier import MODEL_KINDS, available_models, load_classifier
from reabvision.pose import ESTIMATORS, make_estimator
from reabvision.session import ExerciseSession

DISPLAY_WIDTH = 960
ICONS = {"squat": "🦵", "lateral_raise": "🙆", "front_raise": "🙋"}
SHORT = {
    "squat": "Fortalece pernas e quadril.",
    "lateral_raise": "Braços sobem pelas laterais.",
    "front_raise": "Braços sobem pela frente.",
}
VIEW_LABEL = {"lateral": "de lado para a câmera", "frontal": "de frente para a câmera"}

st.set_page_config(
    page_title="Monitor de Reabilitação",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; max-width: 1300px; }
      .rv-counter { background: #1A2126; border-radius: 16px; padding: 18px 20px;
                    text-align: center; margin-bottom: 12px; }
      .rv-counter .label { font-size: 0.95rem; opacity: 0.7; letter-spacing: .05em;
                           text-transform: uppercase; }
      .rv-counter .value { font-size: 4.5rem; font-weight: 700; line-height: 1.1; }
      .rv-card { border-radius: 14px; padding: 14px 18px; margin-bottom: 12px;
                 font-size: 1.15rem; font-weight: 600; }
      .rv-ok { background: rgba(61, 190, 160, .18); border: 1px solid #3DBEA0; }
      .rv-bad { background: rgba(235, 87, 87, .18); border: 1px solid #EB5757; }
      .rv-neutral { background: #1A2126; border: 1px solid #2B353C; font-weight: 400;
                    opacity: .8; }
      .rv-warn { background: rgba(242, 201, 76, .15); border: 1px solid #F2C94C; }
      .rv-sub { font-size: .9rem; font-weight: 400; opacity: .8; margin-top: 4px; }
      .rv-hints { margin: 0; padding-left: 1.2rem; }
      .rv-hints li { margin-bottom: 4px; }
      .rv-fps { font-size: .8rem; opacity: .5; }
      [data-testid="stHeaderActionElements"] { display: none; }
      .st-key-reload_cams button { width: 40px; height: 40px; min-height: 40px;
                                   padding: 0; border: 1px solid #2B353C;
                                   border-radius: 8px; }
      .rv-howto { border: 1px solid #2B353C; border-radius: 16px; padding: 24px; }
      .rv-howto-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 18px; }
      .rv-steps { display: grid; gap: 14px;
                  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
      .rv-step { background: #1A2126; border-radius: 12px; padding: 16px 18px; }
      .rv-step-icon { font-size: 1.6rem; line-height: 1; margin-bottom: 10px; }
      .rv-step-label { font-size: .75rem; font-weight: 600; letter-spacing: .08em;
                       text-transform: uppercase; color: #3DBEA0; margin-bottom: 6px; }
      .rv-step-text { font-size: 1rem; line-height: 1.5; }
      div.stButton > button { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60, show_spinner=False)
def cached_cameras() -> list[tuple[int, str]]:
    return list_cameras()


ss = st.session_state
ss.setdefault("page", "aviso")
ss.setdefault("exercise", None)
ss.setdefault("running", False)
exercises = load_exercises()


# ====================================================================== configurações avançadas
with st.sidebar:
    st.header("⚙️ Configurações avançadas", anchor=False)
    st.caption("Opções técnicas. Os valores padrão servem para o uso normal.")
    estimator_name = st.selectbox(
        "Modelo de pose", list(ESTIMATORS), format_func=lambda k: ESTIMATORS[k]
    )
    ex_for_models = ss.exercise or EXERCISES[0]
    # RF e LSTM ficam escondidos: nos vídeos de câmera comum acertaram só 0–30%
    # (regras: 85–100%). Para testar, rode com REABVISION_EXPERIMENTAL=1.
    if os.environ.get("REABVISION_EXPERIMENTAL"):
        model_options = ["regras", *available_models(ex_for_models)]
        model_kind = st.selectbox(
            "Avaliação da repetição (experimental)",
            model_options,
            format_func=lambda k: "Regras" if k == "regras" else MODEL_KINDS[k],
        )
    else:
        model_kind = "regras"
    source = st.radio("Fonte do vídeo", ["Webcam", "Arquivo de vídeo"])
    if source == "Webcam":
        cameras = cached_cameras()
        cam_col, reload_col = st.columns([5, 1], gap="small", vertical_alignment="bottom")
        with cam_col:
            if cameras:
                names = dict(cameras)
                cam_index = st.selectbox("Câmera", list(names), format_func=names.get)
            else:
                st.warning("Nenhuma câmera encontrada.")
                cam_index = 0
        with reload_col:
            if st.button(
                "", icon=":material/refresh:", key="reload_cams", help="Procurar câmeras de novo"
            ):
                cached_cameras.clear()
                st.rerun()
        resolution = st.selectbox("Resolução", ["640x480", "1280x720"])
        mirror = st.checkbox("Espelhar imagem", value=True)
        uploaded = None
    else:
        uploaded = st.file_uploader("Vídeo", type=["mp4", "mov", "avi", "mkv"])
        cam_index, resolution, mirror = 0, "640x480", False
    show_fps = st.checkbox("Mostrar FPS", value=True)

config_key = (ss.exercise, estimator_name, model_kind, source)


def reset_session() -> None:
    old = ss.pop("session", None)
    if old is not None:
        old.close()
    ss.pop("config_key", None)


def go(page: str, **kw) -> None:
    ss.running = False
    ss.page = page
    for k, v in kw.items():
        ss[k] = v
    st.rerun()


# ====================================================================== 1. aviso
if ss.page == "aviso":
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.title("🩺 Monitor de Reabilitação", anchor=False)
        st.markdown(
            "Acompanhe seus exercícios de fisioterapia pela câmera do computador: "
            "o sistema **conta as repetições** e indica se cada uma foi **bem executada**."
        )
        with st.container(border=True):
            st.markdown(
                "**Antes de começar**\n\n"
                "- Esta ferramenta é um projeto acadêmico de **apoio** à prática orientada por "
                "um fisioterapeuta. **Ela não faz diagnóstico nem prescreve exercícios.**\n"
                "- Interrompa o exercício se sentir dor.\n"
                "- O vídeo da câmera é processado **apenas neste computador** e não é salvo "
                "nem enviado a lugar nenhum."
            )
        if st.button("Entendi, vamos começar", type="primary", use_container_width=True):
            go("escolha")
    st.stop()


# ====================================================================== 2. escolha do exercício
if ss.page == "escolha" or ss.exercise is None:
    st.title("Qual exercício você vai fazer?", anchor=False)
    cols = st.columns(len(EXERCISES))
    for col, key in zip(cols, EXERCISES, strict=True):
        cfg = exercises[key]
        # height="stretch" iguala a altura dos cartões; "distribute" empurra o botão para baixo.
        with col, st.container(border=True, height="stretch", vertical_alignment="distribute"):
            with st.container():
                st.markdown(
                    f"<div style='font-size:3rem'>{ICONS[key]}</div>", unsafe_allow_html=True
                )
                st.subheader(cfg.name, anchor=False)
                st.caption(f"{SHORT[key]} Câmera {VIEW_LABEL[cfg.camera_view]}.")
            if st.button("Escolher", key=f"pick_{key}", use_container_width=True):
                reset_session()
                go("exercicio", exercise=key)
    st.stop()


# ====================================================================== 3. exercício
cfg = exercises[ss.exercise]
if ss.get("config_key") != config_key:
    reset_session()

top_l, top_r = st.columns([4, 1])
with top_l:
    st.title(f"{ICONS[cfg.key]} {cfg.name}", anchor=False)
with top_r:
    st.write("")
    if st.button("← Trocar exercício", use_container_width=True):
        reset_session()
        go("escolha")

col_video, col_panel = st.columns([3, 1.2], gap="large")

with col_panel:
    if ss.running:
        if st.button("■  Parar", type="primary", use_container_width=True, key="stop"):
            ss.running = False
            st.rerun()
    else:
        started = ss.get("session") is not None
        label = "▶  Continuar" if started else "▶  Começar"
        if st.button(label, type="primary", use_container_width=True, key="start"):
            ss.running = True
            st.rerun()
        if started and st.button("↺  Nova série", use_container_width=True, key="restart"):
            reset_session()
            st.rerun()
    counter_box = st.empty()
    verdict_box = st.empty()
    hints_box = st.empty()
    status_box = st.empty()

with col_video:
    frame_box = st.empty()


def card(text: str, kind: str, sub: str = "") -> str:
    sub_html = f"<div class='rv-sub'>{html.escape(sub)}</div>" if sub else ""
    return f"<div class='rv-card rv-{kind}'>{html.escape(text)}{sub_html}</div>"


def render_panel(session: ExerciseSession | None, message: str | None = None) -> None:
    count = session.counter.count if session else 0
    counter_box.markdown(
        f"<div class='rv-counter'><div class='label'>Repetições</div>"
        f"<div class='value'>{count}</div></div>",
        unsafe_allow_html=True,
    )
    last = session.reps[-1] if session and session.reps else None
    if last is None:
        verdict = card("Aguardando a primeira repetição…", "neutral")
    elif not last.counted:
        verdict = card("Movimento não contado", "warn")
    else:
        conf = f" · {last.confidence:.0%} de confiança" if last.confidence is not None else ""
        if last.correct:
            verdict = card(f"✓ Repetição {last.index}: boa execução", "ok", f"Avaliação{conf}")
        else:
            verdict = card(f"✗ Repetição {last.index}: precisa ajustar", "bad", f"Avaliação{conf}")
    verdict_box.markdown(verdict, unsafe_allow_html=True)

    if last is not None and last.hints:
        items = "".join(f"<li>{html.escape(h)}</li>" for h in last.hints)
        hints_box.markdown(f"<ul class='rv-hints'>{items}</ul>", unsafe_allow_html=True)
    else:
        hints_box.empty()

    parts = []
    if message:
        parts.append(card(f"⚠ {message}", "warn"))
    if show_fps and session is not None and ss.running:
        parts.append(f"<div class='rv-fps'>{session.fps:.0f} FPS · {session.estimator.name}</div>")
    status_box.markdown("".join(parts), unsafe_allow_html=True)


def render_summary(session: ExerciseSession) -> None:
    s = session.summary()
    if s.total == 0 and s.not_counted == 0:
        return
    with st.container(border=True):
        st.subheader("Resumo da série", anchor=False)
        c1, c2, c3 = st.columns(3)
        c1.metric("Repetições", s.total)
        c2.metric("Boa execução", s.correct)
        c3.metric("Precisam ajustar", s.incorrect)
        if s.not_counted:
            st.caption(f"{s.not_counted} movimento(s) não contado(s) por estarem incompletos.")
        if s.top_hints:
            st.markdown("**Pontos de atenção**")
            for hint, n in s.top_hints:
                st.markdown(f"- {hint} ({n}×)")


def render_howto() -> None:
    steps = [
        ("📷", "Câmera", cfg.camera),
        ("📏", "Distância", cfg.distance),
        ("🏃", "Movimento", cfg.movement),
        (
            "💡",
            "Ambiente",
            "Bem iluminado, sem luz forte atrás de você. Roupa que deixe ver o contorno do corpo.",
        ),
    ]
    tiles = "".join(
        f"<div class='rv-step'><div class='rv-step-icon'>{icon}</div>"
        f"<div class='rv-step-label'>{label}</div>"
        f"<div class='rv-step-text'>{html.escape(text)}</div></div>"
        for icon, label, text in steps
    )
    frame_box.markdown(
        f"<div class='rv-howto'><div class='rv-howto-title'>Como se posicionar</div>"
        f"<div class='rv-steps'>{tiles}</div></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------- parado
if not ss.running:
    session = ss.get("session")
    render_panel(session, ss.pop("ended_msg", None))
    if session is None:
        render_howto()
    else:
        with frame_box.container():
            render_summary(session)
    st.stop()


# ---------------------------------------------------------------------- rodando
if source == "Arquivo de vídeo" and uploaded is None:
    ss.running = False
    st.sidebar.warning("Escolha um arquivo de vídeo aqui.")
    with frame_box:
        st.warning("Escolha um arquivo de vídeo nas configurações avançadas (barra lateral).")
    st.stop()

if "session" not in ss or source == "Arquivo de vídeo":
    reset_session()
    with frame_box, st.spinner("Preparando a câmera e o modelo…"):
        classifier = None if model_kind == "regras" else load_classifier(cfg.key, model_kind)
        ss.session = ExerciseSession(
            cfg,
            make_estimator(estimator_name),
            classifier,
            logger=logger_from_env(cfg.key, estimator_name),
        )
    ss.config_key = config_key
session: ExerciseSession = ss.session


def open_capture():
    """Retorna (captura, arquivo temporário a apagar, fps do arquivo ou None)."""
    if source == "Webcam":
        cap = cv2.VideoCapture(int(cam_index))
        w, h = map(int, resolution.split("x"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        return cap, None, None
    tmp = tempfile.NamedTemporaryFile(suffix=os.path.splitext(uploaded.name)[1], delete=False)
    tmp.write(uploaded.getbuffer())
    tmp.close()
    cap = cv2.VideoCapture(tmp.name)
    return cap, tmp.name, cap.get(cv2.CAP_PROP_FPS) or 30.0


cap, tmp_path, file_fps = open_capture()
ended_msg = None
try:
    if not cap.isOpened():
        ss.running = False
        frame_box.error(
            "Não foi possível abrir a câmera. Feche outros programas que estejam usando a "
            "câmera ou escolha outra câmera nas configurações avançadas."
        )
        st.stop()
    render_panel(session)
    frame_idx, last_panel, start = 0, 0.0, time.perf_counter()
    while True:
        ok, frame = cap.read()
        if not ok:
            ended_msg = "A câmera parou de enviar imagens." if source == "Webcam" else None
            break
        state = session.process(frame, frame_idx / file_fps if file_fps else None)
        frame_idx += 1

        draw_skeleton(frame, state.pose, state.valid)
        if mirror:
            frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        if w > DISPLAY_WIDTH:
            frame = cv2.resize(frame, (DISPLAY_WIDTH, int(h * DISPLAY_WIDTH / w)))
        frame_box.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        now = time.perf_counter()
        if state.new_rep is not None or now - last_panel > 0.5:
            render_panel(session, state.message)
            last_panel = now

        if file_fps:  # arquivo: reproduz em velocidade real
            delay = frame_idx / file_fps - (time.perf_counter() - start)
            if delay > 0:
                time.sleep(delay)
finally:
    cap.release()
    if tmp_path:
        os.unlink(tmp_path)

# Fim do vídeo ou falha da câmera: volta ao estado parado e mostra o resumo.
ss.running = False
if ended_msg:
    ss.ended_msg = ended_msg
st.rerun()

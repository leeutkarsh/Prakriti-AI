"""
app.py

Streamlit entry point: `streamlit run app.py`

Wires together:
  * streamlit-webrtc (browser webcam -> Python video frames)
  * camera_stream.VideoProcessor (OpenCV + MediaPipe + the gesture state
    machine, running in streamlit-webrtc's own background thread)
  * viewer_server.py (a local Flask server serving the existing, unmodified
    offline_field_viewer/ 3D viewer + the /gesture endpoint it polls)
  * a Streamlit UI: live camera preview, gesture/debug status, the embedded
    3D viewer, and the field-information panel

Run once, locally: `pip install -r requirements.txt` (needs internet once),
then `python download_model.py` (needs internet once), then
`streamlit run app.py` -- no internet required after that.
"""

from __future__ import annotations

import time

import streamlit as st

import config
from shared_state import gesture_state
from viewer_server import start_viewer_server_once

st.set_page_config(
    page_title="Prakriti-AI · Gesture Field Viewer",
    page_icon="🖐️",
    layout="wide",
)

col11, col22 = st.columns(2, gap="medium")

with col11:
    st.video(
        "intro.mp4",
        width=720,
        loop=True,
        autoplay=True,
    )

with col22:
    st.caption("FIELD CAPTURE")
    st.subheader("Drone-Recorded Rice Blast")
    st.write(
        "Drone footage of a rice field affected by Rice Blast, "
        "used to generate the 3D farm digital twin."
    )
# ---------------------------------------------------------------------------
# Styling -- a light dark-HUD theme matching offline_field_viewer/style.css,
# so the Streamlit chrome around the embedded viewer doesn't clash with it.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    html, body, .stApp {
        background: radial-gradient(circle at 50% 0%, #10161a 0%, #060809 55%, #050708 100%);
        color: #ffffff;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    section.main > div { padding-top: 1.2rem; }

    /* Consistent rounded "glass" look for the video/iframe panels */
    video, iframe {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.10);
        box-shadow: 0 8px 30px rgba(0,0,0,.35);
    }
    
    header[data-testid="stHeader"] {
    background: rgba(5, 7, 8, 0.85) !important;
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,.06) !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 12px;
        padding: 10px 14px;
        transition: background .25s ease, border-color .25s ease;
    }
    div[data-testid="stMetric"]:hover {
        background: rgba(255,255,255,.07);
        border-color: rgba(255,255,255,.16);
    }
    div[data-testid="stMetricValue"] { font-size: 1.1rem; }

    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,.08);
        background: rgba(255,255,255,.03);
        overflow: hidden;
    }

    hr { border-color: rgba(255,255,255,.08); }

    .stCheckbox, .stButton > button, button {
        transition: all .18s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0,0,0,.35);
    }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,.15);
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.25); }

    .gesture-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.15);
        background: rgba(255,255,255,.06);
        font-size: 13px;
        letter-spacing: .04em;
        margin-right: 8px;
        transition: background .2s ease;
    }
    .gesture-badge b { color: #69d391; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Gesture-Controlled 3D Field Viewer")
st.caption("Pinch to zoom · Point for field info · Index + middle finger to rotate")


# ---------------------------------------------------------------------------
# Startup checks -- fail loudly but gracefully, and let whatever still works
# keep working (e.g. the 3D viewer works fine even if the hand-tracking
# model hasn't been downloaded yet).
# ---------------------------------------------------------------------------

missing_files = [str(p) for p in config.REQUIRED_FILES if not p.is_file()]
if missing_files:
    st.error(
        "Missing required viewer file(s):\n\n"
        + "\n".join(f"- `{p}`" for p in missing_files)
        + "\n\nMake sure `offline_field_viewer/` (with its `assets/` folder containing "
        "`fused.glb` and `model-viewer.min.js`) is next to `app.py`."
    )
    st.stop()

model_ready = config.HAND_LANDMARKER_MODEL_PATH.is_file()
if not model_ready:
    st.warning(
        f"Hand-tracking model not found at `{config.HAND_LANDMARKER_MODEL_PATH}`. "
        "The 3D viewer below will still work, but gesture control won't. "
        "Run `python download_model.py` once (needs internet), then restart the app."
    )

try:
    from streamlit_webrtc import RTCConfiguration, WebRtcMode, webrtc_streamer
except ImportError:
    st.error(
        "The `streamlit-webrtc` package isn't installed. Run "
        "`pip install -r requirements.txt` and restart the app."
    )
    st.stop()

try:
    import camera_stream
except ImportError as exc:
    st.error(
        f"Couldn't import the camera pipeline ({exc}). Run "
        "`pip install -r requirements.txt` and restart the app."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Start the local viewer HTTP server exactly once per process.
# ---------------------------------------------------------------------------

start_viewer_server_once()

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

cam_col, viewer_col = st.columns([1, 1.35], gap="large")

with cam_col:
    st.subheader("Live Camera")

    debug_mode = st.checkbox("Debug mode (landmarks + tracking details)", value=False)

    rtc_configuration = RTCConfiguration({"iceServers": []})  # local/offline: no STUN/TURN needed

    webrtc_ctx = webrtc_streamer(
        key="gesture-camera",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=camera_stream.video_processor_factory,
        async_processing=True,
    )

    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.debug = debug_mode

    if not model_ready:
        st.caption("Camera preview will run once started, but gestures need the model above.")
    elif not webrtc_ctx.state.playing:
        st.caption("Click **Start** above and allow camera access to begin.")

    status_placeholder = st.empty()

with viewer_col:
    st.subheader("3D Farm Viewer")
    st.components.v1.iframe(config.VIEWER_SERVER_URL, height=560, scrolling=False)
    st.caption(
        "Drag / scroll also work directly on the viewer. Gestures control the same camera."
    )


# ---------------------------------------------------------------------------
# Gesture status + field information panel
# ---------------------------------------------------------------------------

st.divider()
info_col, debug_col = st.columns([1, 1], gap="large")

state = gesture_state.get()

with info_col:
    st.subheader("Field Information")
    if state.get("gesture") == "pointing" and state.get("point_info"):
        info = state["point_info"]
        has_content = any(info.get(k) for k in ("title", "description", "status", "details"))
        if has_content:
            st.markdown(f"**{info.get('title') or 'Field Information'}**")
            if info.get("status"):
                st.caption(info["status"])
            if info.get("description"):
                st.write(info["description"])
            if info.get("details"):
                st.caption(info["details"])
        else:
            st.info("Point gesture detected. Populate `config.POINT_INFORMATION` to show content here.")
    else:
        st.caption("Hold the **point** gesture (index finger extended) at the camera to show field info here.")

with debug_col:
    st.subheader("Status")

    hand_detected = state.get("hand_detected", False)
    gesture_label = state.get("gesture", "none").upper()
    confidence = state.get("confidence", 0.0)
    fps = state.get("fps", 0.0)

    m1, m2, m3 = st.columns(3)
    m1.metric("Hand detected", "YES" if hand_detected else "NO")
    m2.metric("Gesture", gesture_label)
    m3.metric("FPS", f"{fps:.0f}")

    if state.get("stale", True) and webrtc_ctx.state.playing:
        st.caption("Waiting for the first camera frame…")

    if debug_mode:
        with st.expander("Raw gesture debug data", expanded=True):
            st.json(state)


# ---------------------------------------------------------------------------
# Lightweight live refresh for the status panel above.
#
# Streamlit only re-runs this script on user interaction by default; the
# gesture state itself is already updated in real time by the background
# webrtc thread (and is always reflected immediately in the video overlay
# when Debug mode is on). This periodic rerun just keeps the *Streamlit*
# widgets (metrics / info panel) reasonably fresh too, without blocking
# interaction -- it intentionally stops once the camera isn't running.
# ---------------------------------------------------------------------------

if webrtc_ctx.state.playing:
    time.sleep(0.4)
    _rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun")
    _rerun()

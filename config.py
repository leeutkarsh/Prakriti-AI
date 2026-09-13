"""
config.py

Central configuration for the gesture-controlled 3D field viewer.

Every tunable value used by the gesture pipeline lives here, in one place,
so the whole system can be re-tuned without touching detection, state-machine,
or rendering code. See README.md for a guide to what each value does and
how to tune it.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (resolved relative to this file, never the current working directory,
# so the app runs correctly regardless of where `streamlit run` is invoked from)
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

VIEWER_DIR = BASE_DIR / "offline_field_viewer"
VIEWER_INDEX_PATH = VIEWER_DIR / "index.html"
GLB_PATH = VIEWER_DIR / "assets" / "fused.glb"
MODEL_VIEWER_JS_PATH = VIEWER_DIR / "assets" / "model-viewer.min.js"

MODELS_DIR = BASE_DIR / "models"
HAND_LANDMARKER_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"

ASSETS_DIR = BASE_DIR / "assets"

REQUIRED_FILES = [
    VIEWER_INDEX_PATH,
    GLB_PATH,
    MODEL_VIEWER_JS_PATH,
]

# ---------------------------------------------------------------------------
# Local viewer HTTP server
#
# This tiny local server (viewer_server.py) does two jobs:
#   1. serves offline_field_viewer/ as static files (so the browser can load
#      index.html / style.css / viewer.js / the model-viewer bundle / the glb)
#   2. answers GET /gesture with the latest gesture command as JSON, which
#      offline_field_viewer/viewer.js already polls every 35ms.
# ---------------------------------------------------------------------------

VIEWER_SERVER_HOST = "127.0.0.1"
VIEWER_SERVER_PORT = 8765
VIEWER_SERVER_URL = f"http://{VIEWER_SERVER_HOST}:{VIEWER_SERVER_PORT}/"

# ---------------------------------------------------------------------------
# MediaPipe HandLandmarker (Tasks API)
# ---------------------------------------------------------------------------

MAX_NUM_HANDS = 1
MIN_HAND_DETECTION_CONFIDENCE = 0.6
MIN_HAND_PRESENCE_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# ---------------------------------------------------------------------------
# Gesture state machine / smoothing / thresholds
#
# Everything below is intentionally collected into one dict, as requested,
# so it can be tuned in one place without touching gesture_detector.py or
# gesture_controller.py.
# ---------------------------------------------------------------------------

GESTURE_CONFIG = {
    # --- Pinch (zoom) hysteresis -----------------------------------------
    # Thumb-tip <-> index-tip distance, normalized by the hand's own palm
    # size (wrist -> middle-finger-MCP), so the threshold stays meaningful
    # regardless of how far the hand is from the camera.
    #
    #   distance < pinch_start_threshold   -> pinch ENGAGES
    #   distance > pinch_release_threshold -> pinch RELEASES
    #
    # release_threshold is intentionally higher than start_threshold; that
    # gap is the hysteresis band that stops the gesture flickering right at
    # the boundary.
    "pinch_start_threshold": 0.42,
    "pinch_release_threshold": 0.58,

    # --- Finger-extension geometry ----------------------------------------
    # A finger counts as "extended" once its fingertip is this many times
    # farther from the wrist than its PIP joint is. >1.0 required so a
    # slightly-bent finger doesn't register as extended.
    "finger_extension_ratio": 1.15,

    # --- Debounce / state-machine stability --------------------------------
    "activation_frames": 3,    # consecutive matching frames to ENTER a state
    "release_frames": 4,       # consecutive non-matching frames to EXIT a state
    "max_missed_frames": 3,    # frames of "no hand" tolerated before forcing NONE

    # --- Smoothing (exponential moving average weight, 0..1) --------------
    # Higher = more responsive / less smooth. Lower = smoother / more laggy.
    "position_smoothing": 0.45,
    "distance_smoothing": 0.35,

    # --- Sensitivity multipliers --------------------------------------------
    # offline_field_viewer/viewer.js already has its own tuned
    # ROTATE_SENSITIVITY / ZOOM_SENSITIVITY constants and its own
    # MIN_RADIUS/MAX_RADIUS clamps -- that existing rotation/zoom logic is
    # intentionally left untouched. These multipliers scale the *reported
    # hand movement* before it ever reaches viewer.js, so the total feel is
    # (viewer.js constant) x (this multiplier). 1.0 = viewer.js's existing
    # feel, unchanged.
    "rotation_sensitivity": 1.0,
    "zoom_sensitivity": 1.0,

    # --- Safety clamps -------------------------------------------------------
    # Caps on the amplified per-frame movement described above, so a fast
    # hand flick or a momentary tracking glitch can't send a huge jump.
    "max_rotation_delta": 0.05,   # per-axis, normalized coordinate units/frame
    "max_zoom_delta": 0.08,       # normalized_distance units/frame
}

# ---------------------------------------------------------------------------
# Point gesture -- information panel content
#
# Gesture recognition never reads these values; it only ever reports
# whether the "pointing" gesture is active. Fill this in whenever you're
# ready -- no gesture-detection or gesture-state code needs to change.
# ---------------------------------------------------------------------------

POINT_INFORMATION = {
"title": "🌾 Rice Blast",
"description": "🍂 A fungal disease that causes diamond-shaped lesions on rice leaves, reducing photosynthesis and potentially affecting crop yield.",
"status": "🔴 High Risk",
"details": "🔬 Caused by the fungus Magnaporthe oryzae. ⚠️ It can spread rapidly under humid conditions and may affect leaves, stems, and panicles. 🌱 Early detection and timely treatment can help prevent major crop losses."
}

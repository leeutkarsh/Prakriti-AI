# Prakriti-AI — Gesture-Controlled 3D Field Viewer

A hand-gesture interface for the existing offline 3D field viewer
(`offline_field_viewer/`, built on `<model-viewer>`), driven by a live
webcam feed through OpenCV + MediaPipe, orchestrated by Streamlit.

```
 Webcam (browser)
      │  streamlit-webrtc
      ▼
 camera_stream.VideoProcessor        (OpenCV: mirror, draw debug overlay)
      │
      ▼
 gesture_detector.GestureDetector    (MediaPipe HandLandmarker → per-frame
      │                               finger states / thumb-index distance)
      ▼
 gesture_controller.GestureController (NONE/PINCH/POINT/ROTATE state machine:
      │                                smoothing, hysteresis, debounce)
      ▼
 shared_state.gesture_state           (thread-safe latest-command box)
      │
      ▼
 viewer_server.py  →  GET /gesture    (local Flask server, polled every 35ms)
      │
      ▼
 offline_field_viewer/viewer.js       (existing, unmodified rotation/zoom
                                        math — only the point-gesture info
                                        panel was added)
```

The 3D viewer itself — model loading, camera setup, lighting, rotation and
zoom math — is the **existing, unmodified** `offline_field_viewer` code.
`viewer.js` already polled a `/gesture` endpoint before any of this project
was added; `viewer_server.py` is simply the other half of that bridge.
The only change made to the viewer is additive: a field-information panel
that appears during the point gesture (see "Point gesture" below).

## Project layout

```
gesture_farm_viewer/
├── app.py                  Streamlit UI + orchestration
├── camera_stream.py        streamlit-webrtc video processor (OpenCV)
├── gesture_detector.py     MediaPipe HandLandmarker wrapper (stateless/frame)
├── gesture_controller.py   NONE/PINCH/POINT/ROTATE state machine (stateful)
├── shared_state.py         thread-safe bridge between the camera thread,
│                           the Flask server, and the Streamlit UI thread
├── viewer_server.py        local Flask server: serves offline_field_viewer/
│                           and GET /gesture
├── config.py               every tunable value, in one place
├── download_model.py       one-time fetch of the MediaPipe hand model
├── requirements.txt
├── models/                 hand_landmarker.task goes here (see Setup)
└── offline_field_viewer/   the existing 3D viewer (unmodified except the
    ├── index.html          point-gesture info panel described below)
    ├── style.css
    ├── viewer.js
    └── assets/
        ├── model-viewer.min.js
        └── fused.glb
```

## Setup

Two one-time steps need internet access. After that, the app runs
completely offline.

```bash
pip install -r requirements.txt      # 1. Python packages
python download_model.py             # 2. MediaPipe hand-tracking model
streamlit run app.py                 # 3. and from now on, offline
```

**Why a separate model download?** Current MediaPipe releases load hand
tracking from a `.task` model file rather than bundling it in the `pip`
package (the older `mediapipe.solutions.hands` API that many tutorials use
no longer ships at all — this project targets the current MediaPipe Tasks
API). Google hosts the official file; `download_model.py` fetches it once
into `models/hand_landmarker.task`. If your environment has no direct
internet access, download it manually on another machine from:

```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

and copy it to `models/hand_landmarker.task`. (If that link ever moves,
search "MediaPipe HandLandmarker model" for the current official URL.)

The app still works without this file — the 3D viewer loads normally —
gesture control just won't be available until the model is present.

## The three gestures

| Gesture | Hand shape | Effect |
|---|---|---|
| **Rotate** | Index + middle finger extended, others folded | Orbits the camera; hand movement maps to rotation |
| **Pinch** | Thumb and index finger brought together | Zooms; spreading apart zooms in, pinching together zooms out (matches `viewer.js`'s existing convention) |
| **Point** | Only the index finger extended | Shows the field-information panel (see below) |

Gestures are a formal state machine (`gesture_controller.py`), not one-shot
triggers: an action only continues while its gesture is held, and stops the
moment it's released. Priority when a hand shape is ambiguous: **Pinch >
Point > Rotate > none**.

## Point gesture — field information panel

`config.POINT_INFORMATION` is intentionally left blank:

```python
POINT_INFORMATION = {
    "title": "",
    "description": "",
    "status": "",
    "details": "",
}
```

Fill in these four strings whenever your field data is ready — nothing
else needs to change. `gesture_controller.py` attaches this dict to every
frame where the point gesture is active; `viewer.js`'s `updateInfoPanel()`
renders it. Until it's filled in, the panel shows a neutral "no information
configured yet" placeholder rather than fake content.

## Tuning

Every threshold lives in `config.GESTURE_CONFIG`. A few worth knowing:

- **`pinch_start_threshold` / `pinch_release_threshold`** — thumb-index
  distance (normalized by palm size) that engages/releases pinch. The gap
  between them is deliberate hysteresis so the gesture doesn't flicker at
  the boundary.
- **`activation_frames` / `release_frames`** — how many consecutive frames
  a hand shape must be held before a gesture starts/stops. Raise these if
  gestures trigger too easily; lower them for a snappier feel.
- **`max_missed_frames`** — how many consecutive "no hand" frames are
  tolerated (a brief MediaPipe tracking blip just pauses the current
  gesture) before it's forced back to `NONE`.
- **`position_smoothing` / `distance_smoothing`** — exponential-moving-
  average weights (0–1). Lower = smoother but laggier.
- **`rotation_sensitivity` / `zoom_sensitivity`** — `offline_field_viewer/
  viewer.js` already has its own tuned `ROTATE_SENSITIVITY` / `ZOOM_SENSITIVITY`
  constants and its own camera-radius clamps; those are left untouched.
  These Python-side multipliers scale the *reported hand movement* before
  it reaches `viewer.js`, so the effective feel is `(viewer.js constant) ×
  (this multiplier)`. `1.0` leaves the viewer's existing feel unchanged.
- **`max_rotation_delta` / `max_zoom_delta`** — per-frame safety clamps so
  a fast hand flick or a tracking glitch can't send a huge camera jump.

## Debug mode

Check **Debug mode** in the sidebar to:
- draw the hand skeleton and gesture/FPS/confidence text directly on the
  video feed (so it's visible in real time, independent of Streamlit's
  rerun cycle), and
- expand a raw JSON panel of the full gesture state (finger states, raw
  distances, state-machine internals).

## Troubleshooting

- **"Missing required viewer file(s)"** — `offline_field_viewer/assets/`
  must contain `fused.glb` and `model-viewer.min.js`, next to `app.py`.
- **Camera won't start / stays black** — allow camera permission in the
  browser; if it still hangs, another app may be holding the webcam.
- **`streamlit-webrtc` connection fails** — this project runs the WebRTC
  peer connection with no STUN/TURN servers (`RTCConfiguration({"iceServers":
  []})`), which is intentional for a fully offline, same-machine demo
  (`streamlit run app.py` and the browser tab on the same computer). If you
  later deploy this somewhere the browser and server aren't on the same
  machine, you'll need to add ICE servers back in `app.py`.
- **Port 8765 already in use** — change `VIEWER_SERVER_PORT` in `config.py`.
- **Gestures feel too sensitive / not sensitive enough** — see Tuning above.
- **"Hand landmark model not found"** on the video feed — run
  `python download_model.py` (see Setup).

## A note on how this was built and verified

This code was written and tested in a sandboxed environment with no
display, no webcam, and no internet access — so the pieces were validated
the ways that were actually possible there, rather than left unverified:

- `gesture_detector.py`'s geometry (`HandGeometry`) and
  `gesture_controller.py`'s full state machine (hysteresis, debounce,
  hand-loss grace period, pinch/rotate/point transitions) were exercised
  with synthetic landmark data and passed.
- `viewer_server.py` was actually run, and its static file serving and
  `GET /gesture` endpoint were hit with real HTTP requests (including a
  range request against the 100MB `.glb`, which returned `206 Partial
  Content` correctly).
- `camera_stream.VideoProcessor.recv()` was run end-to-end (with a stub
  in place of the real webcam frame source) through detection → state
  machine → shared state → debug overlay drawing, with no errors.
- The MediaPipe API calls target the **Tasks API**
  (`mediapipe.tasks.python.vision.HandLandmarker`), confirmed against a
  real MediaPipe 0.10.33 install — the older `mediapipe.solutions.hands`
  API used in most tutorials is no longer importable in current releases.

What **wasn't** possible to verify directly: an actual webcam feed through
a real browser, `streamlit-webrtc`'s live connection, and Streamlit's own
rendering. Those pieces follow their documented, standard usage patterns,
but give the first run a bit of extra attention — in particular, if your
installed `streamlit-webrtc` version is very new or very old, its
`video_processor_factory` callback API has stayed stable for a long time,
but check its changelog if `app.py` fails to start.

"""
gesture_detector.py

Wraps MediaPipe's HandLandmarker (the current Tasks API -- the older
`mediapipe.solutions.hands` API used in most tutorials no longer ships in
current MediaPipe releases) and turns raw landmarks into a small,
*stateless*, per-frame description of the hand: which fingers are
extended, the thumb-index distance, and a reference point to track.

This module deliberately knows nothing about gesture history, hysteresis,
or the NONE/PINCH/POINT/ROTATE state machine -- that lives in
gesture_controller.py. Keeping the split means either side can be changed
(new gestures, a different detector/model) without touching the other.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

import config


# ---------------------------------------------------------------------------
# MediaPipe hand landmark indices (21-point hand topology).
#
# The legacy `mediapipe.solutions.hands.HandLandmark` enum is not available
# in current MediaPipe (Tasks-API-only) releases, so the indices are
# declared directly here. They follow MediaPipe's standard, unchanged hand
# topology: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
# ---------------------------------------------------------------------------

WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_MCP = 5
INDEX_FINGER_PIP = 6
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9
MIDDLE_FINGER_PIP = 10
MIDDLE_FINGER_TIP = 12
RING_FINGER_PIP = 14
RING_FINGER_TIP = 16
PINKY_PIP = 18
PINKY_TIP = 20

# Re-exported so camera_stream.py can draw a debug skeleton without
# reaching into mediapipe.tasks internals itself.
HAND_CONNECTIONS = [
    (c.start, c.end) for c in vision.HandLandmarksConnections.HAND_CONNECTIONS
]

Landmark = Tuple[float, float, float]


@dataclass
class HandFrame:
    """Everything gesture_controller.py needs about a single video frame."""

    detected: bool
    landmarks: Optional[List[Landmark]] = None
    handedness: Optional[str] = None
    confidence: float = 0.0

    # Normalized [0, 1] image-space position used to track hand translation
    # (the wrist -- stable regardless of which fingers are extended).
    point_x: Optional[float] = None
    point_y: Optional[float] = None

    # Thumb-tip <-> index-tip distance, normalized by palm size so it's
    # meaningful regardless of hand distance from the camera.
    thumb_index_distance: Optional[float] = None

    index_extended: bool = False
    middle_extended: bool = False
    ring_extended: bool = False
    pinky_extended: bool = False


def _dist(a: Landmark, b: Landmark) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


class HandGeometry:
    """Pure landmark-geometry helpers. Kept static/stateless so they're easy
    to unit-test without a webcam, a model file, or MediaPipe itself."""

    @staticmethod
    def is_finger_extended(
        landmarks: List[Landmark],
        pip_idx: int,
        tip_idx: int,
        ratio: float,
        wrist_idx: int = WRIST,
    ) -> bool:
        """A finger is "extended" once its tip sits `ratio` times farther
        from the wrist than its PIP joint does. Distance-from-wrist (rather
        than raw y-coordinate) keeps this reasonably robust to hand tilt
        and rotation in front of the camera."""

        wrist = landmarks[wrist_idx]
        pip = landmarks[pip_idx]
        tip = landmarks[tip_idx]

        pip_dist = _dist(wrist, pip)
        if pip_dist < 1e-6:
            return False

        tip_dist = _dist(wrist, tip)
        return tip_dist > pip_dist * ratio

    @staticmethod
    def palm_size(landmarks: List[Landmark]) -> float:
        size = _dist(landmarks[WRIST], landmarks[MIDDLE_FINGER_MCP])
        return size if size > 1e-6 else 1e-6

    @staticmethod
    def thumb_index_distance(landmarks: List[Landmark]) -> float:
        raw = _dist(landmarks[THUMB_TIP], landmarks[INDEX_FINGER_TIP])
        return raw / HandGeometry.palm_size(landmarks)


class GestureDetector:
    """Runs MediaPipe HandLandmarker on RGB frames and extracts HandFrame data.

    One instance should be created per camera pipeline (it holds a loaded
    model + monotonically increasing internal timestamp, both required by
    MediaPipe's VIDEO running mode) and reused across frames -- do not
    construct a new GestureDetector per frame.
    """

    def __init__(self, model_path: Optional[str] = None):
        resolved_path = str(model_path or config.HAND_LANDMARKER_MODEL_PATH)

        if not Path(resolved_path).is_file():
            raise FileNotFoundError(
                f"MediaPipe hand landmark model not found at: {resolved_path}\n"
                "Run `python download_model.py` once (requires internet the "
                "first time only) to fetch it, then re-run the app offline."
            )

        base_options = BaseOptions(model_asset_path=resolved_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MIN_HAND_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_HAND_PRESENCE_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._start_time = time.monotonic()
        self._last_timestamp_ms = -1

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _next_timestamp_ms(self) -> int:
        # VIDEO running mode requires strictly increasing timestamps; guard
        # against duplicate/backwards timestamps under fast frame rates.
        ts = int((time.monotonic() - self._start_time) * 1000)
        if ts <= self._last_timestamp_ms:
            ts = self._last_timestamp_ms + 1
        self._last_timestamp_ms = ts
        return ts

    def process(self, frame_rgb: np.ndarray) -> HandFrame:
        """`frame_rgb` must be an RGB uint8 numpy array of shape (H, W, 3)."""

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = self._next_timestamp_ms()

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.hand_landmarks:
            return HandFrame(detected=False)

        raw_landmarks = result.hand_landmarks[0]
        landmarks: List[Landmark] = [(lm.x, lm.y, lm.z) for lm in raw_landmarks]

        handedness = None
        confidence = 0.0
        if result.handedness and result.handedness[0]:
            top = result.handedness[0][0]
            handedness = top.category_name
            confidence = float(top.score)

        ratio = config.GESTURE_CONFIG["finger_extension_ratio"]

        return HandFrame(
            detected=True,
            landmarks=landmarks,
            handedness=handedness,
            confidence=confidence,
            point_x=landmarks[WRIST][0],
            point_y=landmarks[WRIST][1],
            thumb_index_distance=HandGeometry.thumb_index_distance(landmarks),
            index_extended=HandGeometry.is_finger_extended(
                landmarks, INDEX_FINGER_PIP, INDEX_FINGER_TIP, ratio
            ),
            middle_extended=HandGeometry.is_finger_extended(
                landmarks, MIDDLE_FINGER_PIP, MIDDLE_FINGER_TIP, ratio
            ),
            ring_extended=HandGeometry.is_finger_extended(
                landmarks, RING_FINGER_PIP, RING_FINGER_TIP, ratio
            ),
            pinky_extended=HandGeometry.is_finger_extended(
                landmarks, PINKY_PIP, PINKY_TIP, ratio
            ),
        )

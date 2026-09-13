"""
camera_stream.py

The webcam/WebRTC/OpenCV side of the pipeline.

VideoProcessor.recv() is called by streamlit-webrtc, in its own managed
background thread, once per incoming browser video frame. It:

  1. converts the frame to a numpy array and mirrors it (so hand movement
     feels natural, per the project requirement)
  2. runs it through GestureDetector -> HandFrame
  3. runs the HandFrame through GestureController -> GestureCommand
  4. publishes that command to shared_state.gesture_state (read by
     viewer_server.py's /gesture endpoint, polled by viewer.js)
  5. optionally draws a debug overlay (landmark skeleton + status text)
     directly onto the returned frame, so gesture status is visible in
     real time without depending on a Streamlit rerun

Using streamlit-webrtc (rather than a raw `cv2.VideoCapture` loop inside
the Streamlit script body) is deliberate: it manages the capture/processing
thread's lifecycle across Streamlit reruns for us, which is exactly the
class of "Streamlit rerun problems / race conditions" this project asks to
avoid.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Optional

import av
import cv2
import numpy as np

from gesture_controller import GestureController
from gesture_detector import GestureDetector, HAND_CONNECTIONS
from shared_state import gesture_state

_LANDMARK_COLOR = (255, 255, 255)
_CONNECTION_COLOR = (105, 211, 145)  # matches the HUD's status-dot green
_TEXT_COLOR = (255, 255, 255)

_GESTURE_LABELS = {
    "none": "NONE",
    "rotate": "ROTATE",
    "pinching": "PINCH",
    "pointing": "POINT",
}


class VideoProcessor:
    """streamlit-webrtc video processor (class-based `recv` API)."""

    def __init__(self) -> None:
        self.debug: bool = False
        self.mirror: bool = True

        self._detector: Optional[GestureDetector] = None
        self._detector_error: Optional[str] = None
        self._controller = GestureController()

        self._frame_times: deque = deque(maxlen=30)

    # -- lazy detector init -------------------------------------------------
    #
    # Constructed lazily (rather than in __init__) so a missing model file
    # surfaces as an on-screen message on the video feed instead of crashing
    # streamlit-webrtc's background thread before the app can render at all.

    def _ensure_detector(self) -> Optional[GestureDetector]:
        if self._detector is not None:
            return self._detector

        if self._detector_error is not None:
            return None

        try:
            self._detector = GestureDetector()
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed
            self._detector_error = str(exc)
            return None

        return self._detector

    # -- main entry point -----------------------------------------------------

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        if self.mirror:
            img = cv2.flip(img, 1)

        now = time.monotonic()
        self._frame_times.append(now)
        fps = self._current_fps()

        detector = self._ensure_detector()

        if detector is None:
            self._draw_setup_error(img)
            gesture_state.update(
                {
                    "gesture": "none",
                    "point_x": 0.5,
                    "point_y": 0.5,
                    "pinch_active": False,
                    "normalized_distance": 1.0,
                    "zoom_direction": None,
                    "hand_detected": False,
                    "confidence": 0.0,
                    "point_info": None,
                    "debug": {"error": self._detector_error},
                },
                fps=fps,
            )
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hand_frame = detector.process(frame_rgb)
        command = self._controller.update(hand_frame)

        gesture_state.update(command.to_dict(), fps=fps)

        if self.debug:
            self._draw_debug_overlay(img, hand_frame, command, fps)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def close(self) -> None:
        if self._detector is not None:
            self._detector.close()

    # -- helpers ----------------------------------------------------------------

    def _current_fps(self) -> float:
        if len(self._frame_times) < 2:
            return 0.0
        span = self._frame_times[-1] - self._frame_times[0]
        if span <= 0:
            return 0.0
        return (len(self._frame_times) - 1) / span

    def _draw_setup_error(self, img: np.ndarray) -> None:
        cv2.putText(
            img,
            "Hand landmark model not found -- run download_model.py",
            (16, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (80, 80, 255),
            2,
            cv2.LINE_AA,
        )

    def _draw_debug_overlay(self, img, hand_frame, command, fps: float) -> None:
        h, w = img.shape[:2]

        if hand_frame.detected and hand_frame.landmarks:
            pts = [(int(x * w), int(y * h)) for x, y, _ in hand_frame.landmarks]

            for start, end in HAND_CONNECTIONS:
                cv2.line(img, pts[start], pts[end], _CONNECTION_COLOR, 2, cv2.LINE_AA)
            for x, y in pts:
                cv2.circle(img, (x, y), 4, _LANDMARK_COLOR, -1, cv2.LINE_AA)

        label = _GESTURE_LABELS.get(command.gesture, command.gesture.upper())
        lines = [
            f"GESTURE: {label}",
            f"HAND: {'YES' if hand_frame.detected else 'NO'}   FPS: {fps:.1f}",
            f"CONF: {command.confidence * 100:.0f}%",
        ]

        debug = command.debug or {}
        if "raw_distance" in debug and debug["raw_distance"] is not None:
            lines.append(f"THUMB-INDEX DIST: {debug['raw_distance']:.3f}")
        fingers = []
        for name in ("index_extended", "middle_extended", "ring_extended", "pinky_extended"):
            if name in debug:
                fingers.append(f"{name.split('_')[0][0].upper()}:{'1' if debug[name] else '0'}")
        if fingers:
            lines.append(" ".join(fingers))

        y0 = 28
        for i, line in enumerate(lines):
            y = y0 + i * 22
            cv2.putText(img, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(img, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, _TEXT_COLOR, 1, cv2.LINE_AA)


def video_processor_factory() -> VideoProcessor:
    return VideoProcessor()

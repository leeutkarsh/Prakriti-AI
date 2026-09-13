"""
shared_state.py

A tiny thread-safe box for the latest gesture command.

Three different threads touch this in the running app:
  * the streamlit-webrtc video callback thread writes a new command to it
    on every processed camera frame (see camera_stream.py)
  * the local Flask viewer server's GET /gesture handler reads it on every
    poll from the browser (see viewer_server.py, polled every 35ms by
    offline_field_viewer/viewer.js)
  * the main Streamlit script thread reads it to render the debug panel

Keeping this in its own module (rather than importing streamlit or Flask
here) means neither of the other two modules has to import the other.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

_DEFAULT_COMMAND: Dict[str, Any] = {
    "gesture": "none",
    "point_x": 0.5,
    "point_y": 0.5,
    "pinch_active": False,
    "normalized_distance": 1.0,
    "zoom_direction": None,
    "hand_detected": False,
    "confidence": 0.0,
    "point_info": None,
    "debug": {"note": "camera not started yet"},
}


class GestureState:
    """Thread-safe holder for the latest gesture command + a few run-time
    stats (fps, last-update time) used by the debug UI."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._command: Dict[str, Any] = dict(_DEFAULT_COMMAND)
        self._last_update_ts: float = 0.0
        self._fps: float = 0.0

    def update(self, command: Dict[str, Any], fps: Optional[float] = None) -> None:
        with self._lock:
            self._command = command
            self._last_update_ts = time.monotonic()
            if fps is not None:
                self._fps = fps

    def get(self) -> Dict[str, Any]:
        with self._lock:
            data = dict(self._command)
            data["fps"] = round(self._fps, 1)
            data["stale"] = (time.monotonic() - self._last_update_ts) > 1.0 if self._last_update_ts else True
            return data

    def reset(self) -> None:
        with self._lock:
            self._command = dict(_DEFAULT_COMMAND)
            self._last_update_ts = 0.0
            self._fps = 0.0


# One process-wide instance. The camera pipeline, the Flask server, and the
# Streamlit UI all import this same object rather than passing it around
# through Streamlit's session state, so it behaves correctly regardless of
# how many browser tabs/sessions are open against this one local demo.
gesture_state = GestureState()

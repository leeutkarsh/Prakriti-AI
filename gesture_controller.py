"""
gesture_controller.py

Turns a stream of per-frame HandFrame objects (from gesture_detector.py)
into a stable NONE / PINCH / POINT / ROTATE gesture state machine, and
produces the JSON-serializable command that offline_field_viewer/viewer.js
polls from GET /gesture.

Everything here is stateful (smoothing, hysteresis, debounce, hand-loss
grace period) and everything tunable lives in config.GESTURE_CONFIG, so
gestures can be re-tuned -- or the whole classifier swapped later -- without
touching gesture_detector.py or the JS/HTTP bridge.

State machine
-------------
    NONE --(sustained pinch shape)--> PINCH
    NONE --(sustained point shape)--> POINT
    NONE --(sustained rotate shape)--> ROTATE
    <active state> --(sustained "none" shape, or hand lost)--> NONE

Each state conceptually has enter/update/exit behavior (see _enter_state /
_update_state / _exit_state) so switching states never leaves stale
per-gesture bookkeeping (e.g. a rotation anchor) lying around to cause a
jump the next time that gesture activates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

import config
from gesture_detector import HandFrame

STATE_NONE = "none"
STATE_PINCH = "pinch"
STATE_POINT = "point"
STATE_ROTATE = "rotate"

# Gesture label -> value viewer.js expects in the "gesture" JSON field.
_GESTURE_JSON_NAME = {
    STATE_NONE: "none",
    STATE_PINCH: "pinching",
    STATE_POINT: "pointing",
    STATE_ROTATE: "rotate",
}


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _ema(previous: Optional[float], new: float, alpha: float) -> float:
    if previous is None:
        return new
    return previous + alpha * (new - previous)


@dataclass
class GestureCommand:
    """JSON-serializable payload polled by offline_field_viewer/viewer.js."""

    gesture: str
    point_x: float
    point_y: float
    pinch_active: bool
    normalized_distance: float
    zoom_direction: Optional[str]
    hand_detected: bool
    confidence: float
    point_info: Optional[dict]
    debug: dict

    def to_dict(self) -> dict:
        return asdict(self)


class GestureController:
    def __init__(self, cfg: Optional[dict] = None):
        self.cfg = cfg or config.GESTURE_CONFIG

        self.state = STATE_NONE

        # EMA-smoothed tracking values, updated every frame a hand is seen.
        self._smoothed_x: Optional[float] = None
        self._smoothed_y: Optional[float] = None
        self._smoothed_distance: Optional[float] = None

        # Pinch hysteresis latch.
        self._pinch_engaged = False

        # Debounce bookkeeping.
        self._pending_candidate = STATE_NONE
        self._pending_count = 0

        # Hand-loss grace period.
        self._missed_frames = 0

        # Per-gesture "enter" bookkeeping used only while that gesture is
        # active (the amplification/clamping trick described in config.py).
        self._rotate_prev_x: Optional[float] = None
        self._rotate_prev_y: Optional[float] = None
        self._rotate_report_x = 0.5
        self._rotate_report_y = 0.5

        self._pinch_prev_distance: Optional[float] = None
        self._pinch_report_distance = 0.5
        self._last_zoom_direction: Optional[str] = None

    # -- public API ---------------------------------------------------

    def update(self, hand_frame: HandFrame) -> GestureCommand:
        if not hand_frame.detected:
            return self._handle_hand_lost()

        self._missed_frames = 0

        self._smoothed_x = _ema(self._smoothed_x, hand_frame.point_x, self.cfg["position_smoothing"])
        self._smoothed_y = _ema(self._smoothed_y, hand_frame.point_y, self.cfg["position_smoothing"])
        self._smoothed_distance = _ema(
            self._smoothed_distance, hand_frame.thumb_index_distance, self.cfg["distance_smoothing"]
        )

        self._update_pinch_hysteresis()
        raw_candidate = self._classify(hand_frame)
        self._advance_state_machine(raw_candidate)

        return self._build_command(hand_frame)

    # -- hand loss ------------------------------------------------------

    def _handle_hand_lost(self) -> GestureCommand:
        self._missed_frames += 1

        # Small grace period: a brief 1-2 frame tracking blip holds the last
        # known command steady (no new delta) instead of visibly killing an
        # in-progress gesture. Sustained loss beyond max_missed_frames still
        # clears the gesture immediately, per the "never leave a gesture
        # active indefinitely" requirement.
        if self.state != STATE_NONE and self._missed_frames <= self.cfg["max_missed_frames"]:
            return self._build_held_command()

        if self.state != STATE_NONE:
            self._exit_state(self.state)
            self.state = STATE_NONE
        self._pinch_engaged = False
        self._pending_candidate = STATE_NONE
        self._pending_count = 0

        return GestureCommand(
            gesture=_GESTURE_JSON_NAME[STATE_NONE],
            point_x=self._smoothed_x if self._smoothed_x is not None else 0.5,
            point_y=self._smoothed_y if self._smoothed_y is not None else 0.5,
            pinch_active=False,
            normalized_distance=self._smoothed_distance if self._smoothed_distance is not None else 1.0,
            zoom_direction=None,
            hand_detected=False,
            confidence=0.0,
            point_info=None,
            debug={
                "state": self.state,
                "missed_frames": self._missed_frames,
                "note": "hand not detected",
            },
        )

    def _build_held_command(self) -> GestureCommand:
        """Re-emit the current gesture's last known values unchanged, with
        no new delta -- used only during the brief hand-loss grace period."""

        gesture_json = _GESTURE_JSON_NAME[self.state]

        if self.state == STATE_ROTATE:
            point_x, point_y = self._rotate_report_x, self._rotate_report_y
        else:
            point_x = self._smoothed_x if self._smoothed_x is not None else 0.5
            point_y = self._smoothed_y if self._smoothed_y is not None else 0.5

        normalized_distance = (
            self._pinch_report_distance if self.state == STATE_PINCH else (self._smoothed_distance or 1.0)
        )
        point_info = dict(config.POINT_INFORMATION) if self.state == STATE_POINT else None

        return GestureCommand(
            gesture=gesture_json,
            point_x=point_x,
            point_y=point_y,
            pinch_active=(self.state == STATE_PINCH),
            normalized_distance=normalized_distance,
            zoom_direction=None,
            hand_detected=False,
            confidence=0.0,
            point_info=point_info,
            debug={
                "state": self.state,
                "missed_frames": self._missed_frames,
                "note": "holding through brief tracking loss",
            },
        )

    # -- classification (priority: PINCH > POINT > ROTATE > NONE) -------

    def _update_pinch_hysteresis(self) -> None:
        distance = self._smoothed_distance
        if distance is None:
            return

        if self._pinch_engaged:
            if distance > self.cfg["pinch_release_threshold"]:
                self._pinch_engaged = False
        else:
            if distance < self.cfg["pinch_start_threshold"]:
                self._pinch_engaged = True

    def _classify(self, hand_frame: HandFrame) -> str:
        if self._pinch_engaged:
            return STATE_PINCH

        if (
            hand_frame.index_extended
            and hand_frame.middle_extended
            and not hand_frame.ring_extended
            and not hand_frame.pinky_extended
        ):
            return STATE_ROTATE

        if (
            hand_frame.index_extended
            and not hand_frame.middle_extended
            and not hand_frame.ring_extended
            and not hand_frame.pinky_extended
        ):
            return STATE_POINT

        return STATE_NONE

    # -- debounce / state machine ----------------------------------------

    def _advance_state_machine(self, raw_candidate: str) -> None:
        if raw_candidate == self.state:
            self._pending_candidate = raw_candidate
            self._pending_count = 0
            return

        if raw_candidate == self._pending_candidate:
            self._pending_count += 1
        else:
            self._pending_candidate = raw_candidate
            self._pending_count = 1

        required = self.cfg["release_frames"] if raw_candidate == STATE_NONE else self.cfg["activation_frames"]

        if self._pending_count >= required:
            self._exit_state(self.state)
            self.state = raw_candidate
            self._enter_state(raw_candidate)
            self._pending_count = 0

    def _enter_state(self, state: str) -> None:
        if state == STATE_ROTATE:
            self._rotate_prev_x = self._smoothed_x
            self._rotate_prev_y = self._smoothed_y
            self._rotate_report_x = self._smoothed_x if self._smoothed_x is not None else 0.5
            self._rotate_report_y = self._smoothed_y if self._smoothed_y is not None else 0.5
        elif state == STATE_PINCH:
            self._pinch_prev_distance = self._smoothed_distance
            self._pinch_report_distance = self._smoothed_distance if self._smoothed_distance is not None else 0.5
            self._last_zoom_direction = None

    def _exit_state(self, state: str) -> None:
        if state == STATE_ROTATE:
            self._rotate_prev_x = None
            self._rotate_prev_y = None
        elif state == STATE_PINCH:
            self._pinch_prev_distance = None
            self._last_zoom_direction = None

    # -- per-frame updates for the currently active gesture ---------------

    def _update_rotate(self) -> None:
        """Advance the reported rotate point by the clamped, sensitivity-
        scaled delta of the real hand movement (see config.py for why)."""

        if self._rotate_prev_x is None or self._smoothed_x is None:
            self._rotate_prev_x = self._smoothed_x
            self._rotate_prev_y = self._smoothed_y
            return

        max_d = self.cfg["max_rotation_delta"]
        sens = self.cfg["rotation_sensitivity"]

        dx = _clamp(self._smoothed_x - self._rotate_prev_x, -max_d, max_d) * sens
        dy = _clamp(self._smoothed_y - self._rotate_prev_y, -max_d, max_d) * sens

        self._rotate_report_x += dx
        self._rotate_report_y += dy

        self._rotate_prev_x = self._smoothed_x
        self._rotate_prev_y = self._smoothed_y

    def _update_pinch(self) -> None:
        """Advance the reported zoom distance by the clamped, sensitivity-
        scaled delta of the real thumb-index distance."""

        if self._pinch_prev_distance is None or self._smoothed_distance is None:
            self._pinch_prev_distance = self._smoothed_distance
            return

        max_d = self.cfg["max_zoom_delta"]
        sens = self.cfg["zoom_sensitivity"]

        delta = _clamp(self._smoothed_distance - self._pinch_prev_distance, -max_d, max_d) * sens
        self._pinch_report_distance += delta
        self._pinch_prev_distance = self._smoothed_distance

        if abs(delta) > 1e-6:
            self._last_zoom_direction = "in" if delta > 0 else "out"

    # -- output -------------------------------------------------------------

    def _build_command(self, hand_frame: HandFrame) -> GestureCommand:
        if self.state == STATE_ROTATE:
            self._update_rotate()
        elif self.state == STATE_PINCH:
            self._update_pinch()

        gesture_json = _GESTURE_JSON_NAME[self.state]

        if self.state == STATE_ROTATE:
            point_x, point_y = self._rotate_report_x, self._rotate_report_y
        else:
            point_x = self._smoothed_x if self._smoothed_x is not None else 0.5
            point_y = self._smoothed_y if self._smoothed_y is not None else 0.5

        normalized_distance = (
            self._pinch_report_distance if self.state == STATE_PINCH else (self._smoothed_distance or 1.0)
        )

        point_info = dict(config.POINT_INFORMATION) if self.state == STATE_POINT else None

        return GestureCommand(
            gesture=gesture_json,
            point_x=_clamp(point_x, 0.0, 1.0) if self.state != STATE_ROTATE else point_x,
            point_y=_clamp(point_y, 0.0, 1.0) if self.state != STATE_ROTATE else point_y,
            pinch_active=(self.state == STATE_PINCH),
            normalized_distance=normalized_distance,
            zoom_direction=self._last_zoom_direction if self.state == STATE_PINCH else None,
            hand_detected=True,
            confidence=hand_frame.confidence,
            point_info=point_info,
            debug={
                "state": self.state,
                "pending_candidate": self._pending_candidate,
                "pending_count": self._pending_count,
                "pinch_engaged": self._pinch_engaged,
                "raw_distance": self._smoothed_distance,
                "handedness": hand_frame.handedness,
                "index_extended": hand_frame.index_extended,
                "middle_extended": hand_frame.middle_extended,
                "ring_extended": hand_frame.ring_extended,
                "pinky_extended": hand_frame.pinky_extended,
            },
        )

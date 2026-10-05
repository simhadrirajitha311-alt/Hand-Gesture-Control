from __future__ import annotations

import time
from typing import Optional


class ActivationManager:
    """Provides a deliberate open-palm activation window before commands are accepted."""

    def __init__(self, hold_duration: float = 1.5):
        self.hold_duration = float(hold_duration)
        self._activation_started_at: Optional[float] = None
        self._active = False
        self._state = "INACTIVE"

    @property
    def state(self) -> str:
        return self._state

    @property
    def is_active(self) -> bool:
        return self._active

    def update(self, gesture_name: Optional[str]) -> str:
        if gesture_name == "OPEN_PALM":
            if self._activation_started_at is None:
                self._activation_started_at = time.monotonic()
            elapsed = time.monotonic() - self._activation_started_at
            if elapsed >= self.hold_duration:
                self._active = True
                self._state = "ACTIVE"
            else:
                self._active = False
                self._state = "ACTIVATING"
            return self._state

        self._activation_started_at = None
        self._active = False
        self._state = "INACTIVE"
        return self._state

    def reset(self) -> None:
        self._activation_started_at = None
        self._active = False
        self._state = "INACTIVE"

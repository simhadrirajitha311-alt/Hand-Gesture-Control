from __future__ import annotations

import time

try:
    import pyautogui
except Exception:  # pragma: no cover - headless test environments
    pyautogui = None


class PresentationController:
    """Sends slide navigation key presses to the active presentation application."""

    def __init__(self, key_bindings: dict[str, str] | None = None, cooldown: float = 0.85):
        self.key_bindings = key_bindings or {"next_slide": "right", "previous_slide": "left"}
        self.cooldown = float(cooldown)
        self._last_action_at = 0.0

    def next_slide(self) -> bool:
        return self._trigger("next_slide")

    def previous_slide(self) -> bool:
        return self._trigger("previous_slide")

    def _trigger(self, action: str) -> bool:
        now = time.monotonic()
        if now - self._last_action_at < self.cooldown:
            return False
        if pyautogui is None:
            self._last_action_at = now
            return False
        key = self.key_bindings.get(action, "right" if action == "next_slide" else "left")
        pyautogui.press(key)
        self._last_action_at = now
        return True

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Optional, Tuple

import numpy as np

try:
    import pyautogui
except Exception:  # pragma: no cover - headless test environments
    pyautogui = None

from src.utils.smoothing import ExponentialSmoother


class MouseController:
    """Maps webcam coordinates to screen coordinates and smooths cursor movement."""

    def __init__(self, sensitivity: float = 1.0, smoothing: float = 0.28, deadzone: float = 0.02):
        self.sensitivity = float(sensitivity)
        self.deadzone = float(deadzone)
        self.smoother = ExponentialSmoother(alpha=smoothing)
        if pyautogui is not None:
            try:
                self.screen_size = pyautogui.size()
            except Exception:
                self.screen_size = SimpleNamespace(width=1920, height=1080)
        else:
            self.screen_size = SimpleNamespace(width=1920, height=1080)
        self.last_position: Optional[Tuple[float, float]] = None
        self.last_click_time = 0.0

    def map_to_screen(self, x: float, y: float, frame_width: int, frame_height: int) -> Tuple[float, float]:
        if frame_width <= 0 or frame_height <= 0:
            return (self.screen_size.width / 2.0, self.screen_size.height / 2.0)
        target_x = (x / frame_width) * self.screen_size.width
        target_y = (y / frame_height) * self.screen_size.height
        return float(target_x), float(target_y)

    def move(self, normalized_x: float, normalized_y: float, frame_width: int, frame_height: int) -> None:
        if pyautogui is None:
            return
        target = self.map_to_screen(normalized_x * frame_width, normalized_y * frame_height, frame_width, frame_height)
        if self.last_position is None:
            self.last_position = target
        dx = target[0] - self.last_position[0]
        dy = target[1] - self.last_position[1]
        distance = np.linalg.norm(np.array([dx, dy], dtype=np.float32))
        if distance <= self.deadzone * max(self.screen_size.width, self.screen_size.height):
            return
        smoothed = self.smoother.update(target)
        pyautogui.moveTo(smoothed[0], smoothed[1], duration=0.0)
        self.last_position = target

    def click(self) -> None:
        if pyautogui is None:
            return
        now = time.monotonic()
        if now - self.last_click_time < 0.45:
            return
        pyautogui.click()
        self.last_click_time = now

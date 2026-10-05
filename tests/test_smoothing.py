from __future__ import annotations

from src.controllers.mouse_controller import MouseController
from src.utils.smoothing import ExponentialSmoother


def test_exponential_smoother_converges():
    smoother = ExponentialSmoother(alpha=0.5)
    first = smoother.update([1.0, 1.0])
    second = smoother.update([2.0, 2.0])
    assert first[0] == 1.0
    assert second[0] < 2.0


def test_mouse_coordinate_mapping():
    mouse = MouseController(sensitivity=1.0, smoothing=0.5, deadzone=0.0)
    x, y = mouse.map_to_screen(320, 240, 640, 480)
    assert x > 0
    assert y > 0

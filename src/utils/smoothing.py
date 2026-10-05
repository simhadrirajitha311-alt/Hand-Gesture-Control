from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np


class ExponentialSmoother:
    """Simple one-dimensional or multi-dimensional smoothing filter."""

    def __init__(self, alpha: float = 0.3):
        self.alpha = float(alpha)
        self.last: Optional[np.ndarray] = None

    def update(self, value: Sequence[float]) -> np.ndarray:
        current = np.asarray(value, dtype=np.float32)
        if self.last is None:
            self.last = current
            return self.last.copy()
        self.last = (self.alpha * current) + ((1.0 - self.alpha) * self.last)
        return self.last.copy()

    def reset(self) -> None:
        self.last = None


class MovingAverage:
    """Basic moving-average smoother for small sequences."""

    def __init__(self, window_size: int = 5):
        self.window_size = max(1, int(window_size))
        self.values: list[float] = []

    def update(self, value: float) -> float:
        self.values.append(float(value))
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return float(sum(self.values) / max(1, len(self.values)))

    def reset(self) -> None:
        self.values.clear()

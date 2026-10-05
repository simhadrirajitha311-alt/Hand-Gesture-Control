from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import numpy as np


Point = Sequence[float]


def euclidean_distance(a: Point, b: Point) -> float:
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))


def midpoint(a: Point, b: Point) -> np.ndarray:
    return (np.asarray(a) + np.asarray(b)) / 2.0


def point_angle(a: Point, b: Point, c: Point) -> float:
    ba = np.asarray(a) - np.asarray(b)
    bc = np.asarray(c) - np.asarray(b)
    cosine = float(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8))
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))


def normalized_point(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
    if width <= 0 or height <= 0:
        return 0.0, 0.0
    return float(x / width), float(y / height)


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def fingers_extended(landmarks: np.ndarray, indices: Iterable[int]) -> list[bool]:
    results: list[bool] = []
    for tip_idx, pip_idx, mcp_idx in indices:
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        mcp = landmarks[mcp_idx]
        score = np.linalg.norm(tip[:2] - mcp[:2])
        extended = bool((tip[1] < pip[1] - 0.02) and (score > 0.04))
        results.append(extended)
    return results


def index_tip_position(landmarks: np.ndarray) -> np.ndarray:
    return np.asarray(landmarks[8], dtype=np.float32)


def thumb_tip_position(landmarks: np.ndarray) -> np.ndarray:
    return np.asarray(landmarks[4], dtype=np.float32)

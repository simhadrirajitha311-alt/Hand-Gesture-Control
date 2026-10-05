from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from src.utils.geometry import euclidean_distance, fingers_extended, index_tip_position, thumb_tip_position


@dataclass
class GestureResult:
    gesture: str = "NONE"
    confidence: float = 0.0
    active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class GestureRecognizer:
    """Recognizes a small, deterministic set of hand gestures from normalized landmarks."""

    def __init__(self, confidence_threshold: float = 0.7, pinch_threshold: float = 0.08):
        self.confidence_threshold = confidence_threshold
        self.pinch_threshold = pinch_threshold

    def detect_open_palm(self, landmarks: np.ndarray) -> GestureResult:
        ext = fingers_extended(landmarks, [(8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17)])
        thumb_open = euclidean_distance(landmarks[4][:2], landmarks[3][:2]) > 0.06
        confidence = float(np.mean(ext + [thumb_open]))
        return GestureResult("OPEN_PALM", confidence, confidence >= self.confidence_threshold, {"thumb_open": thumb_open})

    def detect_one_finger(self, landmarks: np.ndarray) -> GestureResult:
        index_ext = landmarks[8][1] < landmarks[6][1] - 0.02
        middle_bent = landmarks[12][1] > landmarks[10][1]
        ring_bent = landmarks[16][1] > landmarks[14][1]
        pinky_bent = landmarks[20][1] > landmarks[18][1]
        confidence = float(np.mean([index_ext, middle_bent, ring_bent, pinky_bent]))
        return GestureResult("ONE_FINGER", confidence, confidence >= self.confidence_threshold, {})

    def detect_two_fingers(self, landmarks: np.ndarray) -> GestureResult:
        index_ext = landmarks[8][1] < landmarks[6][1] - 0.02
        middle_ext = landmarks[12][1] < landmarks[10][1] - 0.02
        ring_bent = landmarks[16][1] > landmarks[14][1]
        pinky_bent = landmarks[20][1] > landmarks[18][1]
        confidence = float(np.mean([index_ext, middle_ext, ring_bent, pinky_bent]))
        return GestureResult("TWO_FINGERS", confidence, confidence >= self.confidence_threshold, {})

    def detect_thumbs_up(self, landmarks: np.ndarray) -> GestureResult:
        thumb_tip = thumb_tip_position(landmarks)
        thumb_ip = landmarks[6]
        index_tip = index_tip_position(landmarks)
        fingers_bent = (index_tip[1] > landmarks[5][1]) and (landmarks[12][1] > landmarks[9][1]) and (landmarks[16][1] > landmarks[13][1]) and (landmarks[20][1] > landmarks[17][1])
        up = bool(thumb_tip[1] < thumb_ip[1] - 0.05)
        confidence = float(np.mean([up, fingers_bent]))
        return GestureResult("THUMBS_UP", confidence, confidence >= self.confidence_threshold, {})

    def detect_thumbs_down(self, landmarks: np.ndarray) -> GestureResult:
        thumb_tip = thumb_tip_position(landmarks)
        thumb_ip = landmarks[6]
        fingers_bent = (landmarks[8][1] > landmarks[5][1]) and (landmarks[12][1] > landmarks[9][1]) and (landmarks[16][1] > landmarks[13][1]) and (landmarks[20][1] > landmarks[17][1])
        down = bool(thumb_tip[1] > thumb_ip[1] + 0.05)
        confidence = float(np.mean([down, fingers_bent]))
        return GestureResult("THUMBS_DOWN", confidence, confidence >= self.confidence_threshold, {})

    def detect_pinch(self, landmarks: np.ndarray) -> GestureResult:
        d = euclidean_distance(landmarks[4][:2], landmarks[8][:2])
        active = d < self.pinch_threshold
        confidence = float(np.clip(1.0 - 0.3 * (d / max(self.pinch_threshold, 1e-6)), 0.0, 1.0))
        return GestureResult("PINCH", confidence, active and confidence >= self.confidence_threshold, {"distance": d})

    def classify(self, landmarks: np.ndarray) -> GestureResult:
        if landmarks is None or landmarks.shape != (21, 3):
            return GestureResult("NONE", 0.0, False, {})

        candidates: List[GestureResult] = [
            self.detect_pinch(landmarks),
            self.detect_thumbs_up(landmarks),
            self.detect_thumbs_down(landmarks),
            self.detect_two_fingers(landmarks),
            self.detect_one_finger(landmarks),
            self.detect_open_palm(landmarks),
        ]
        candidates = [result for result in candidates if result.active]
        if not candidates:
            return GestureResult("NONE", 0.0, False, {})
        return max(candidates, key=lambda item: item.confidence)


# Convenience functions for tests and external usage.
def detect_open_palm(landmarks: np.ndarray, confidence_threshold: float = 0.7) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold).detect_open_palm(landmarks)


def detect_one_finger(landmarks: np.ndarray, confidence_threshold: float = 0.7) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold).detect_one_finger(landmarks)


def detect_two_fingers(landmarks: np.ndarray, confidence_threshold: float = 0.7) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold).detect_two_fingers(landmarks)


def detect_thumbs_up(landmarks: np.ndarray, confidence_threshold: float = 0.7) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold).detect_thumbs_up(landmarks)


def detect_thumbs_down(landmarks: np.ndarray, confidence_threshold: float = 0.7) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold).detect_thumbs_down(landmarks)


def detect_pinch(landmarks: np.ndarray, confidence_threshold: float = 0.7, pinch_threshold: float = 0.06) -> GestureResult:
    return GestureRecognizer(confidence_threshold=confidence_threshold, pinch_threshold=pinch_threshold).detect_pinch(landmarks)

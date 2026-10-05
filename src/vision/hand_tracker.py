from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError as exc:  # pragma: no cover - environment handles installation
    raise RuntimeError("mediapipe is required for desktop hand tracking. Install requirements.txt first.") from exc


class HandTracker:
    """Wraps MediaPipe hand landmark detection for the desktop application."""

    def __init__(self, max_hands: int = 1, detection_confidence: float = 0.5, tracking_confidence: float = 0.5):
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self.logger = logging.getLogger(__name__)
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        if frame is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            return None
        hand = results.multi_hand_landmarks[0]
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand.landmark], dtype=np.float32)
        return landmarks

    def draw(self, frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        if frame is None or landmarks is None:
            return frame
        h, w = frame.shape[:2]
        for idx, point in enumerate(landmarks):
            x = int(point[0] * w)
            y = int(point[1] * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
        return frame

    def close(self) -> None:
        self.hands.close()
        self.logger.info("MediaPipe hands closed.")

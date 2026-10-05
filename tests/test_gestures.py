from __future__ import annotations

import numpy as np

from src.vision.gesture_recognizer import GestureRecognizer


def _make_open_palm() -> np.ndarray:
    landmarks = np.zeros((21, 3), dtype=np.float32)
    for idx in range(21):
        landmarks[idx] = [0.5, 0.7, 0.0]
    landmarks[4] = [0.38, 0.62, 0.0]
    landmarks[8] = [0.6, 0.14, 0.0]
    landmarks[12] = [0.7, 0.18, 0.0]
    landmarks[16] = [0.82, 0.24, 0.0]
    landmarks[20] = [0.9, 0.30, 0.0]
    landmarks[6] = [0.53, 0.38, 0.0]
    landmarks[10] = [0.66, 0.42, 0.0]
    landmarks[14] = [0.76, 0.46, 0.0]
    landmarks[18] = [0.86, 0.50, 0.0]
    return landmarks


def _make_thumbs_up() -> np.ndarray:
    landmarks = np.zeros((21, 3), dtype=np.float32)
    for idx in range(21):
        landmarks[idx] = [0.5, 0.75, 0.0]
    landmarks[4] = [0.36, 0.20, 0.0]
    landmarks[8] = [0.6, 0.82, 0.0]
    landmarks[12] = [0.72, 0.84, 0.0]
    landmarks[16] = [0.8, 0.86, 0.0]
    landmarks[20] = [0.9, 0.88, 0.0]
    landmarks[6] = [0.42, 0.36, 0.0]
    return landmarks


def _make_pinch() -> np.ndarray:
    landmarks = np.zeros((21, 3), dtype=np.float32)
    for idx in range(21):
        landmarks[idx] = [0.5, 0.75, 0.0]
    landmarks[4] = [0.44, 0.50, 0.0]
    landmarks[8] = [0.47, 0.53, 0.0]
    return landmarks


def test_open_palm_detection():
    recognizer = GestureRecognizer(confidence_threshold=0.7)
    result = recognizer.detect_open_palm(_make_open_palm())
    assert result.gesture == "OPEN_PALM"
    assert result.active is True


def test_thumbs_up_detection():
    recognizer = GestureRecognizer(confidence_threshold=0.7)
    result = recognizer.detect_thumbs_up(_make_thumbs_up())
    assert result.gesture == "THUMBS_UP"
    assert result.active is True


def test_pinch_detection():
    recognizer = GestureRecognizer(confidence_threshold=0.7, pinch_threshold=0.06)
    result = recognizer.detect_pinch(_make_pinch())
    assert result.gesture == "PINCH"
    assert result.active is True


def test_classify_returns_highest_confidence():
    recognizer = GestureRecognizer(confidence_threshold=0.7)
    result = recognizer.classify(_make_open_palm())
    assert result.gesture == "OPEN_PALM"

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AppConfig:
    """Central configuration for the desktop hand gesture system."""

    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    display_width: int = 1920
    display_height: int = 1080
    activation_hold_duration: float = 1.5
    gesture_confidence_threshold: float = 0.7
    cursor_sensitivity: float = 1.0
    cursor_smoothing: float = 0.28
    cursor_deadzone: float = 0.02
    pinch_threshold: float = 0.08
    pinch_cooldown: float = 0.45
    volume_step: int = 5
    gesture_cooldown: float = 0.9
    max_hands: int = 1
    detection_confidence: float = 0.5
    tracking_confidence: float = 0.5
    key_bindings: Dict[str, str] = field(
        default_factory=lambda: {
            "next_slide": "right",
            "previous_slide": "left",
        }
    )


def get_config() -> AppConfig:
    return AppConfig()

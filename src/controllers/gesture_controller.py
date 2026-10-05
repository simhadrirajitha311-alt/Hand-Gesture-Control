from __future__ import annotations

import logging
import time
from typing import Optional

from src.controllers.mouse_controller import MouseController
from src.controllers.presentation_controller import PresentationController
from src.controllers.volume_controller import VolumeController
from src.safety.activation_manager import ActivationManager
from src.vision.gesture_recognizer import GestureResult


class GestureController:
    """Dispatches recognized actions after activation and cooldown checks."""

    def __init__(
        self,
        mouse_controller: Optional[MouseController] = None,
        volume_controller: Optional[VolumeController] = None,
        presentation_controller: Optional[PresentationController] = None,
        activation_manager: Optional[ActivationManager] = None,
        gesture_cooldown: float = 0.8,
    ):
        self.mouse_controller = mouse_controller
        self.volume_controller = volume_controller
        self.presentation_controller = presentation_controller
        self.activation_manager = activation_manager
        self.gesture_cooldown = float(gesture_cooldown)
        self.logger = logging.getLogger(__name__)
        self._last_command_at = 0.0

    def dispatch(self, gesture_result: GestureResult, frame_width: int = 640, frame_height: int = 480) -> dict:
        if gesture_result.gesture == "NONE":
            return {"executed": False, "reason": "No valid gesture"}

        if self.activation_manager is not None:
            activation_state = self.activation_manager.update(gesture_result.gesture)
            if activation_state != "ACTIVE":
                return {"executed": False, "state": activation_state, "gesture": gesture_result.gesture}

        if time.monotonic() - self._last_command_at < self.gesture_cooldown:
            return {"executed": False, "reason": "Cooldown active"}

        gesture = gesture_result.gesture
        if gesture == "THUMBS_UP" and self.volume_controller is not None:
            self.volume_controller.increase()
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "volume_up"}
        if gesture == "THUMBS_DOWN" and self.volume_controller is not None:
            self.volume_controller.decrease()
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "volume_down"}
        if gesture == "TWO_FINGERS" and self.presentation_controller is not None:
            self.presentation_controller.next_slide()
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "next_slide"}
        if gesture == "ONE_FINGER" and self.presentation_controller is not None:
            self.presentation_controller.previous_slide()
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "previous_slide"}
        if gesture == "PINCH" and self.mouse_controller is not None:
            self.mouse_controller.click()
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "mouse_click"}
        if gesture == "OPEN_PALM":
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "activation"}

        # Allow index-tip tracking when a single extended index finger is present.
        if self.mouse_controller is not None and gesture_result.metadata.get("index_tip") is not None:
            x, y = gesture_result.metadata["index_tip"]
            self.mouse_controller.move(x, y, frame_width, frame_height)
            self._last_command_at = time.monotonic()
            return {"executed": True, "action": "mouse_move"}

        return {"executed": False, "reason": "Unhandled gesture"}

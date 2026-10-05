from __future__ import annotations

import argparse
import logging
import time

import cv2
import numpy as np

from config import get_config
from src.camera.camera_manager import CameraManager
from src.controllers.gesture_controller import GestureController
from src.controllers.mouse_controller import MouseController
from src.controllers.presentation_controller import PresentationController
from src.controllers.volume_controller import VolumeController
from src.safety.activation_manager import ActivationManager
from src.vision.gesture_recognizer import GestureRecognizer
from src.vision.hand_tracker import HandTracker


logger = logging.getLogger(__name__)


def _is_index_tracking(landmarks: np.ndarray) -> bool:
    if landmarks is None or landmarks.shape != (21, 3):
        return False
    if landmarks[8][1] >= landmarks[6][1] - 0.02:
        return False
    if landmarks[12][1] > landmarks[10][1]:
        return False
    if landmarks[16][1] > landmarks[14][1]:
        return False
    if landmarks[20][1] > landmarks[18][1]:
        return False
    return True


def _draw_status(frame: np.ndarray, gesture_name: str, activation_state: str) -> None:
    cv2.putText(frame, f"Gesture: {gesture_name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Status: {activation_state}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)


def run_desktop() -> None:
    config = get_config()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    camera = CameraManager(camera_index=config.camera_index, width=config.camera_width, height=config.camera_height)
    hand_tracker = HandTracker(
        max_hands=config.max_hands,
        detection_confidence=config.detection_confidence,
        tracking_confidence=config.tracking_confidence,
    )
    recognizer = GestureRecognizer(confidence_threshold=config.gesture_confidence_threshold, pinch_threshold=config.pinch_threshold)
    activation_manager = ActivationManager(hold_duration=config.activation_hold_duration)
    mouse_controller = MouseController(sensitivity=config.cursor_sensitivity, smoothing=config.cursor_smoothing, deadzone=config.cursor_deadzone)
    volume_controller = VolumeController(step=config.volume_step)
    presentation_controller = PresentationController(key_bindings=config.key_bindings, cooldown=config.gesture_cooldown)
    gesture_controller = GestureController(
        mouse_controller=mouse_controller,
        volume_controller=volume_controller,
        presentation_controller=presentation_controller,
        activation_manager=activation_manager,
        gesture_cooldown=config.gesture_cooldown,
    )

    try:
        camera.open()
        while True:
            ok, frame = camera.read()
            if not ok or frame is None:
                logger.warning("Camera frame was empty. Retrying.")
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            landmarks = hand_tracker.detect(frame)
            gesture_name = "NONE"
            activation_state = activation_manager.state

            if landmarks is not None:
                result = recognizer.classify(landmarks)
                gesture_name = result.gesture
                activation_state = activation_manager.update(result.gesture)
                if activation_state == "ACTIVE":
                    if result.gesture in {"THUMBS_UP", "THUMBS_DOWN", "TWO_FINGERS", "ONE_FINGER", "PINCH"}:
                        gesture_controller.dispatch(result, frame.shape[1], frame.shape[0])
                    elif _is_index_tracking(landmarks):
                        index_x, index_y = float(landmarks[8][0]), float(landmarks[8][1])
                        mouse_controller.move(index_x, index_y, frame.shape[1], frame.shape[0])
                elif result.gesture == "OPEN_PALM":
                    _draw_status(frame, gesture_name, activation_state)
            else:
                activation_manager.reset()

            frame = hand_tracker.draw(frame, landmarks) if landmarks is not None else frame
            _draw_status(frame, gesture_name, activation_state)

            cv2.imshow("Hand Gesture Control", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    finally:
        camera.close()
        hand_tracker.close()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Desktop hand gesture control system")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera device index")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = get_config()
    if args.camera_index != 0:
        config.camera_index = args.camera_index
    run_desktop()

from __future__ import annotations

import logging
from typing import Optional, Tuple

import cv2
import numpy as np


class CameraManager:
    """Thin wrapper around OpenCV webcam capture."""

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.logger = logging.getLogger(__name__)
        self.capture: Optional[cv2.VideoCapture] = None

    def open(self) -> cv2.VideoCapture:
        capture = cv2.VideoCapture(self.camera_index)
        if not capture.isOpened():
            raise RuntimeError(
                "Unable to access the webcam. Check that the camera is connected and not being used by another application."
            )
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture = capture
        self.logger.info("Camera opened with index %s", self.camera_index)
        return capture

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.capture is None:
            raise RuntimeError("Camera is not open. Call open() before read().")
        ok, frame = self.capture.read()
        if not ok or frame is None:
            return False, None
        return True, frame

    def close(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            self.logger.info("Camera closed.")

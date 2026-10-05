from __future__ import annotations

import logging
import os
import platform
import subprocess
from typing import Optional


class VolumeController:
    """Cross-platform-ish wrapper for system volume controls."""

    def __init__(self, step: int = 5):
        self.step = int(step)
        self.logger = logging.getLogger(__name__)
        self.platform_name = platform.system().lower()

    def increase(self) -> bool:
        return self._apply_delta(self.step)

    def decrease(self) -> bool:
        return self._apply_delta(-self.step)

    def _apply_delta(self, delta: int) -> bool:
        current = self.get_volume()
        if current is None:
            return False
        target = max(0, min(100, current + delta))
        return self.set_volume(target)

    def get_volume(self) -> Optional[int]:
        if self.platform_name == "linux":
            if self._command_exists("pactl"):
                return self._parse_pactl_volume(self._run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]))
            if self._command_exists("amixer"):
                result = self._run(["amixer", "get", "Master"])
                return self._parse_amixer_volume(result)
        elif self.platform_name == "darwin":
            if self._command_exists("osascript"):
                result = self._run(["osascript", "-e", 'output volume of (get volume settings)'])
                return self._parse_int(result)
        elif self.platform_name == "windows":
            return None
        return None

    def set_volume(self, target: int) -> bool:
        target = max(0, min(100, int(target)))
        if self.platform_name == "linux":
            if self._command_exists("pactl"):
                return self._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{target}%"], check=False)
            if self._command_exists("amixer"):
                return self._run(["amixer", "-M", "sset", "Master", f"{target}%"], check=False)
        elif self.platform_name == "darwin":
            if self._command_exists("osascript"):
                return self._run(["osascript", "-e", f"set volume output volume {target}"], check=False)
        elif self.platform_name == "windows":
            self.logger.warning("Windows volume control is not implemented in this environment. Use a platform-specific backend if needed.")
            return False
        self.logger.warning("No supported system-volume backend is available for %s.", self.platform_name)
        return False

    def _command_exists(self, command: str) -> bool:
        return subprocess.run(["bash", "-lc", f"command -v {command} >/dev/null 2>&1"], check=False).returncode == 0

    def _run(self, args, check: bool = True) -> Optional[str]:
        try:
            completed = subprocess.run(args, capture_output=True, text=True, check=check)
            if completed.returncode != 0:
                return None
            return completed.stdout.strip() or completed.stderr.strip() or None
        except (FileNotFoundError, OSError):
            return None

    @staticmethod
    def _parse_pactl_volume(output: Optional[str]) -> Optional[int]:
        if output is None:
            return None
        try:
            parts = [item.strip() for item in output.split("/")]
            if len(parts) >= 2:
                return int(float(parts[1].split('%')[0]))
        except (IndexError, ValueError):
            return None
        return None

    @staticmethod
    def _parse_amixer_volume(output: Optional[str]) -> Optional[int]:
        if output is None:
            return None
        try:
            for token in output.split():
                if token.endswith("%"):
                    return int(float(token.rstrip("%")))
        except ValueError:
            return None
        return None

    @staticmethod
    def _parse_int(output: Optional[str]) -> Optional[int]:
        if output is None:
            return None
        try:
            return int(float(output.strip()))
        except ValueError:
            return None

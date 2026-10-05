from __future__ import annotations

from src.safety.activation_manager import ActivationManager


def test_activation_requires_hold_time(monkeypatch):
    manager = ActivationManager(hold_duration=1.5)
    monkeypatch.setattr("time.monotonic", lambda: 0.0)
    assert manager.update("OPEN_PALM") == "ACTIVATING"
    monkeypatch.setattr("time.monotonic", lambda: 2.0)
    assert manager.update("OPEN_PALM") == "ACTIVE"
    assert manager.is_active is True


def test_activation_resets_on_non_open_palm():
    manager = ActivationManager(hold_duration=1.5)
    manager.update("OPEN_PALM")
    assert manager.update("NONE") == "INACTIVE"
    assert manager.is_active is False

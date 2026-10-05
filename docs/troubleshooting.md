# Troubleshooting

## Camera access issues

- Verify that no other app is already using the webcam.
- Confirm the browser has camera permissions in the web demo.
- Try a different camera index in the desktop app using `--camera-index`.

## No hand detected

- Improve lighting.
- Hold the hand slightly above the camera.
- Ensure the hand is fully visible inside the frame.
- Avoid background clutter that resembles a hand.

## Gesture misfires

- Use the required activation gesture before the command set is enabled.
- Keep the palm stable during the activation window.
- Reduce jitter by keeping the hand steady.

## Volume backend problems

- On Linux, `pactl` or `amixer` is preferred.
- On macOS, `osascript` is used.
- Windows volume automation is intentionally isolated and may require a platform-specific backend.

## Presentation control issues

- Ensure the target application accepts keyboard input from the foreground window.
- Check the configured key mappings in `config.py`.

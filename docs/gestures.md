# Gesture reference

This project supports a compact, safety-first gesture vocabulary.

| Gesture | Action | Geometric cues |
| --- | --- | --- |
| OPEN PALM | Activation / safety gate | Fingers extended; palm open; holds for ~1.5s |
| THUMBS UP | Volume up | Thumb extended upward; remaining fingers curled |
| THUMBS DOWN | Volume down | Thumb extended downward; remaining fingers curled |
| TWO FINGERS | Next slide | Index and middle extended; ring + pinky curled |
| ONE FINGER | Previous slide | Index only extended; other fingers curled |
| PINCH | Mouse click | Thumb tip and index tip close within pinch threshold |
| INDEX TIP TRACKING | Mouse motion | Index finger extended while other fingers are bent |

## Geometric logic

The recognizer relies on a mix of normalized landmark positions and relative geometry:

- Finger extension is estimated from the relative vertical position of the fingertip and proximal joint.
- Thumb direction is inferred from thumb-tip motion relative to the thumb IP landmark.
- Pinch strength is measured by Euclidean distance between thumb tip and index tip.
- Cursor movement is mapped from normalized screen-space index-tip coordinates to the active display using smoothing.

These calculations are intentionally configured with thresholds rather than raw constants embedded across the runtime code.

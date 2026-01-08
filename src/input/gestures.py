"""
src/input/gestures.py

Classifies hand poses from MediaPipe landmarks into semantic game commands.
Determines gesture based on finger extension states (0-5 fingers or neutral).

Note: This module provides only the classification logic.
The gesture interpretation (what actions they trigger) is handled in main.py
to allow flexible gesture mapping per game state.
"""


class GestureRecognizer:
    """Static helper class to interpret hand poses into game commands."""

    @staticmethod
    def classify(landmarks):
        """
        Analyzes finger states to determine the gesture.

        MediaPipe Landmark Indices:
            - Tips: [Index(8), Middle(12), Ring(16), Pinky(20)]
            - PIPs (Knuckles): [Index(6), Middle(10), Ring(14), Pinky(18)]
            - Thumb Tip: 4
            - Wrist: 0

        Args:
            landmarks: MediaPipe hand landmarks object

        Returns:
            String representation of gesture: "0"-"5" (finger count) or "neutral"
        """
        if not landmarks:
            return "neutral"

        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        count = 0

        # Check four fingers (raised if tip is higher than pip)
        # Note: Y-coordinates are smaller at the top of the screen
        for t, p in zip(tips, pips):
            if landmarks.landmark[t].y < landmarks.landmark[p].y:
                count += 1

        # Check Thumb
        # Simple heuristic: Horizontal distance from wrist (0) to tip (4)
        # Determines if the thumb is extended outward
        if abs(landmarks.landmark[4].x - landmarks.landmark[0].x) > 0.1:
            count += 1

        return str(count)
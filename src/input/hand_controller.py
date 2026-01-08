"""
src/input/hand_controller.py

Processes camera input and calculates paddle control angles from hand tracking.
Integrates MediaPipe hand detection with gesture recognition and pause detection.
"""

import cv2
import math
import mediapipe as mp

from src.core.utils import calculate_angle, ExponentialMovingAverage
from src.input.gestures import GestureRecognizer
from config import (
    DOMINANT_HAND,
    PAUSE_TOGGLE_ENABLED,
    PAUSE_ACTIVATION_TIME,
    TRACKING_TARGET_POINT,
    TRACKING_ANCHOR_POINT,
)


class HandController:
    """Handles hand tracking and converts hand position to paddle control input."""

    def __init__(self):
        """Initialize MediaPipe hand detection and smoothing filters."""
        # Setup MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,  # Balanced between speed and accuracy
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Smoothing filter for angle data
        # Starts with alpha=0.2, adjusted dynamically during processing
        self.smoother = ExponentialMovingAverage(alpha=0.2)

        self.current_angle = 140.0

        # Tracking states
        self.pause_timer = 0.0
        self.pause_threshold = PAUSE_ACTIVATION_TIME
        self.current_gesture = "neutral"
        self.raw_landmarks = []
        self.hands_detected = False

    def process(self, frame_bgr, dt):
        """
        Process video frame to detect hands and calculate paddle control angle.

        Args:
            frame_bgr: OpenCV frame (BGR format)
            dt: Delta time since last frame (seconds)

        Returns:
            Dictionary with keys: 'angle', 'gesture', 'pause_progress'
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        self.raw_landmarks = []
        self.hands_detected = False
        pause_progress = 0.0
        output_gesture = "neutral"

        if results.multi_hand_landmarks and results.multi_handedness:
            self.hands_detected = True
            self.raw_landmarks = results.multi_hand_landmarks

            # Check if user initiates pause gesture (X-pose with two hands)
            if PAUSE_TOGGLE_ENABLED and len(results.multi_hand_landmarks) == 2:
                if self._check_x_pose(
                    results.multi_hand_landmarks[0], results.multi_hand_landmarks[1]
                ):
                    self.pause_timer += dt
                    pause_progress = min(1.0, self.pause_timer / self.pause_threshold)
                else:
                    self.pause_timer = 0.0

            # Track only the dominant hand for paddle control
            found_dominant = False
            for idx, hand_handedness in enumerate(results.multi_handedness):
                label = hand_handedness.classification[0].label

                if label == DOMINANT_HAND:
                    found_dominant = True
                    lms = results.multi_hand_landmarks[idx]

                    # Extract target point (usually Thumb Tip)
                    p_target_obj = lms.landmark[TRACKING_TARGET_POINT]
                    target_x, target_y = p_target_obj.x, p_target_obj.y

                    # Extract anchor point (Pivot)
                    # Handles both single points and calculated midpoints
                    if isinstance(TRACKING_ANCHOR_POINT, tuple):
                        # Config is a tuple (e.g., (5, 6)), calculate midpoint
                        p1 = lms.landmark[TRACKING_ANCHOR_POINT[0]]
                        p2 = lms.landmark[TRACKING_ANCHOR_POINT[1]]
                        anchor_x = (p1.x + p2.x) / 2
                        anchor_y = (p1.y + p2.y) / 2
                    else:
                        # Config is a single landmark index
                        p_anchor = lms.landmark[TRACKING_ANCHOR_POINT]
                        anchor_x, anchor_y = p_anchor.x, p_anchor.y

                    # Calculate raw angle between anchor and target
                    raw_angle = calculate_angle(
                        (anchor_x, anchor_y), (target_x, target_y)
                    )

                    # Apply adaptive smoothing to reduce jitter
                    # Small changes (holding still) use low alpha (0.15) for smoothness
                    # Large changes (fast movement) use high alpha (up to 0.9) for responsiveness
                    diff = abs(raw_angle - self.current_angle)
                    target_alpha = 0.15 + min(diff / 10.0, 1.0) * 0.75
                    self.smoother.alpha = target_alpha
                    self.current_angle = self.smoother.update(raw_angle)

                    # Classify hand gesture (finger count)
                    output_gesture = GestureRecognizer.classify(lms)
                    self.current_gesture = output_gesture

                    break

            # Reset pause if dominant hand not found
            if not found_dominant:
                self.pause_timer = 0.0

        else:
            # No hands detected - reset pause and gesture
            self.pause_timer = 0.0
            output_gesture = "neutral"

        return {
            "angle": self.current_angle,
            "gesture": output_gesture,
            "pause_progress": pause_progress,
        }

    def _check_x_pose(self, hand1_lms, hand2_lms):
        """
        Check if both hands form an X-pose (pause gesture).

        Logic: Wrists are far apart, but index fingers are close together.

        Args:
            hand1_lms: First hand landmarks from MediaPipe
            hand2_lms: Second hand landmarks from MediaPipe

        Returns:
            True if X-pose detected, False otherwise
        """
        h1_idx = hand1_lms.landmark[8]  # Index finger tip
        h2_idx = hand2_lms.landmark[8]  # Index finger tip
        h1_wrist = hand1_lms.landmark[0]  # Wrist
        h2_wrist = hand2_lms.landmark[0]  # Wrist

        tip_dist = math.hypot(h1_idx.x - h2_idx.x, h1_idx.y - h2_idx.y)
        wrist_dist = math.hypot(h1_wrist.x - h2_wrist.x, h1_wrist.y - h2_wrist.y)

        return tip_dist < 0.15 and wrist_dist > 0.20

    def draw_debug(self, frame):
        """
        Draw hand skeleton overlay for debugging purposes.

        Args:
            frame: OpenCV frame to draw on

        Returns:
            Frame with hand landmarks drawn
        """
        for lms in self.raw_landmarks:
            self.mp_draw.draw_landmarks(frame, lms, self.mp_hands.HAND_CONNECTIONS)
        return frame

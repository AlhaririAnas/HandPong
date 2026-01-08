"""
src/core/utils.py

Mathematical helpers and signal processing utilities for the game engine.
Provides angle calculations, coordinate mapping, and smoothing filters.
"""

import math


def clamp(value, min_val, max_val):
    """
    Restrict a value to be within a specific range.

    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def calculate_angle(point1, point2):
    """
    Calculate the angle in degrees between two points (0-360).

    Inverts Y axis calculation because screen coordinates grow downwards.

    Args:
        point1: Tuple (x, y) for first point
        point2: Tuple (x, y) for second point

    Returns:
        Angle in degrees (0-360)
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dy = -dy  # Invert Y for standard Cartesian behavior

    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)

    return angle_deg % 360


def map_angle_to_paddle_y(angle_deg, game_height, paddle_height, angle_up, angle_down):
    """
    Map a hand angle (degrees) to a vertical Y position on the game board.

    Handles clamping and interpolation between the defined angular range.

    Args:
        angle_deg: Angle in degrees
        game_height: Height of the game area
        paddle_height: Height of the paddle
        angle_up: Angle value corresponding to top position
        angle_down: Angle value corresponding to bottom position

    Returns:
        Y position relative to game area top
    """
    angle_deg = angle_deg % 360
    max_y = game_height - paddle_height

    # Clamp input to the effective operational range
    if angle_deg < angle_up:
        angle_deg = angle_up
    elif angle_deg > angle_down:
        angle_deg = angle_down

    # Calculate interpolation factor
    if angle_down != angle_up:
        progress = (angle_deg - angle_up) / (angle_down - angle_up)
    else:
        progress = 0.5

    return progress * max_y


class ExponentialMovingAverage:
    """
    Smooths noisy input data (like hand tracking coordinates).

    Uses exponential smoothing with support for adaptive alpha to balance
    between responsiveness and smoothness.
    """

    def __init__(self, alpha=0.1):
        """
        Initialize the smoothing filter.

        Args:
            alpha: Smoothing factor (0.0 to 1.0)
                   Lower alpha = more smoothing, higher alpha = more responsive
        """
        self.alpha = alpha
        self.value = 0.0
        self.initialized = False

    def update(self, new_value):
        """
        Add a new data point and return the smoothed average.

        Args:
            new_value: New measurement to smooth

        Returns:
            Smoothed value
        """
        if not self.initialized:
            self.value = new_value
            self.initialized = True
            return new_value

        self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        return self.value

    def reset(self):
        """Reset the filter state."""
        self.value = 0.0
        self.initialized = False
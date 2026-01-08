"""
utils.py - Updated with v4.6 Paddle Control Logic

Utility functions including the original map_angle_to_paddle_y from v4.6.
"""

import math
import colorsys


def calculate_angle(point1, point2):
    """
    Calculate angle in degrees between two points.
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def map_angle_to_paddle_y(angle_deg, game_height, paddle_height, 
                          angle_up=150.0, angle_down=230.0, 
                          deadzone_range=(175, 185)):
    """
    Map hand angle to paddle Y position using ORIGINAL v4.6 logic.
    
    Args:
        angle_deg: Hand angle in degrees (0-360)
        game_height: Height of game area in pixels
        paddle_height: Height of paddle in pixels
        angle_up: Angle threshold for UP direction (default 150Â°)
        angle_down: Angle threshold for DOWN direction (default 230Â°)
        deadzone_range: (min, max) angle for neutral zone (default 175-185Â°)
    
    Returns:
        (paddle_y, is_in_deadzone): tuple of paddle Y position and deadzone flag
    """
    deadzone_min, deadzone_max = deadzone_range
    
    # Normalize angle to 0-360 range
    angle_deg = angle_deg % 360
    
    # Available space for paddle movement
    max_y = game_height - paddle_height
    center_y = max_y / 2.0
    
    # Check if in deadzone (neutral zone around 180Â°)
    if deadzone_min <= angle_deg <= deadzone_max:
        # Neutral - return center position
        return center_y, True
    
    # UP DIRECTION (angle between angle_up and 180)
    if angle_up <= angle_deg < 180:
        # Linear interpolation from angle_up to 180
        # angle_up (150Â°) â†’ position 0 (top)
        # 180Â° â†’ position center_y (middle)
        progress = (angle_deg - angle_up) / (180.0 - angle_up)
        paddle_y = (1.0 - progress) * 0 + progress * center_y
        return paddle_y, False
    
    # DOWN DIRECTION (angle between 180 and angle_down)
    if 180 < angle_deg <= angle_down:
        # Linear interpolation from 180 to angle_down
        # 180Â° â†’ position center_y (middle)
        # angle_down (230Â°) â†’ position max_y (bottom)
        progress = (angle_deg - 180.0) / (angle_down - 180.0)
        paddle_y = progress * max_y + (1.0 - progress) * center_y
        return paddle_y, False
    
    # EXTREME ANGLES (outside 150-230 range)
    if angle_deg < angle_up:
        # Full UP
        return 0, False
    else:
        # Full DOWN
        return max_y, False


def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def get_hsv_color(hue_normalized):
    """
    Convert HSV color to RGB.
    
    Args:
        hue_normalized: Hue value between 0.0 and 1.0
    
    Returns:
        (R, G, B) tuple in 0-255 range
    """
    h = hue_normalized % 1.0  # Ensure in 0-1 range
    s = 0.8  # Saturation (0.8 = 80%)
    v = 0.95  # Value/Brightness (0.95 = 95%)
    
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


class ExponentialMovingAverage:
    """Smooth values using exponential moving average."""
    
    def __init__(self, alpha=0.1):
        """
        Args:
            alpha: Smoothing factor (0-1). Higher = more responsive.
        """
        self.alpha = alpha
        self.value = 0.0
        self.initialized = False
    
    def update(self, new_value):
        """Update and return smoothed value."""
        if not self.initialized:
            self.value = new_value
            self.initialized = True
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        
        return self.value
    
    def reset(self):
        """Reset the filter."""
        self.value = 0.0
        self.initialized = False
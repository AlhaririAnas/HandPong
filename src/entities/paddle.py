"""
src/entities/paddle.py

Player and AI paddle logic, including movement smoothing and PowerUp states.
Manages paddle position, collisions, and active powerup effects.
"""

import pygame
from config import (
    GAME_AREA_Y,
    GAME_AREA_HEIGHT,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    COLOR_P1,
    COLOR_P2,
)
from src.core.utils import clamp


class Paddle:
    """Manages paddle physics, movement, and powerup effects."""

    def __init__(self, x, is_ai=False):
        """
        Initialize a paddle at the specified position.

        Args:
            x: X coordinate for paddle position
            is_ai: Boolean indicating if this is AI-controlled paddle
        """
        self.rect = pygame.Rect(x, GAME_AREA_Y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.is_ai = is_ai
        self.color = COLOR_P2 if is_ai else COLOR_P1
        self.score = 0

        self.active_powerup_text = None
        self.powerup_end_time = 0.0

        self.is_trampoline = False
        self.has_agility = False

        self.trail_history = []

    def reset(self):
        """Reset position, score, and all active effects."""
        self.score = 0
        self.clear_powerups()
        self.rect.centery = GAME_AREA_Y + GAME_AREA_HEIGHT // 2
        self.trail_history.clear()

    def clear_powerups(self):
        """Remove all active powerups immediately."""
        self.active_powerup_text = None
        self.rect.height = PADDLE_HEIGHT
        self.is_trampoline = False
        self.has_agility = False

    def move(self, target_y):
        """
        Move the paddle towards the target Y position.

        AI uses Lerp (Linear Interpolation) for smoothness.
        Player uses direct mapping for responsiveness.

        Args:
            target_y: Target Y position
        """
        min_y = GAME_AREA_Y
        max_y = GAME_AREA_Y + GAME_AREA_HEIGHT - self.rect.height
        target_y = clamp(target_y, min_y, max_y)

        if self.is_ai:
            self.rect.y = target_y - (self.rect.y - target_y) * 0.15
        else:
            self.rect.y = target_y

        if self.has_agility:
            self.trail_history.append(self.rect.copy())
            if len(self.trail_history) > 12:
                self.trail_history.pop(0)
        else:
            self.trail_history.clear()

    def update(self, current_time):
        """
        Update paddle state and check for powerup expiration.

        Args:
            current_time: Current game time in seconds
        """
        if self.active_powerup_text and current_time > self.powerup_end_time:
            self.clear_powerups()

    def apply_powerup(self, ptype, name, duration, current_time):
        """
        Apply a specific powerup effect to the paddle.

        Args:
            ptype: Powerup type ("enlarge", "shrink", "trampoline", "agility")
            name: Display name of the powerup
            duration: Duration of the powerup effect in seconds
            current_time: Current game time in seconds
        """
        self.clear_powerups()

        self.active_powerup_text = name
        self.powerup_end_time = current_time + duration

        if ptype == "enlarge":
            self.rect.height = int(PADDLE_HEIGHT * 1.5)
        elif ptype == "shrink":
            self.rect.height = int(PADDLE_HEIGHT * 0.5)
        elif ptype == "trampoline":
            self.is_trampoline = True
            self.rect.height = 120
        elif ptype == "agility":
            self.has_agility = True

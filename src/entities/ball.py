"""
src/entities/ball.py

Handles ball physics, collision detection, and visual state modifiers (Ghost, Tiny).
Manages ball movement, wall bounces, and powerup effects.
Ball modifiers (Ghost, Tiny) persist across game rounds until duration expires.
"""

import pygame
import random

from config import (
    GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT,
    BALL_START_SPEED, BALL_RADIUS
)


class Ball:
    """Manages ball physics, collisions, and visual state modifiers."""

    def __init__(self):
        """Initialize ball with default position and state."""
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0

        self.is_tiny = False
        self.is_ghost = False
        self.ghost_visible = True
        self.modifier_end_time = 0.0

        self.reset()

    def reset(self):
        """
        Reset ball to center with random initial direction.

        Note: Does NOT reset modifiers (Ghost/Tiny) - they persist across rounds.
        Modifiers only reset when their duration expires.
        """
        self.x = GAME_AREA_X + GAME_AREA_WIDTH // 2
        self.y = GAME_AREA_Y + GAME_AREA_HEIGHT // 2

        direction = random.choice([-1, 1])
        self.vx = BALL_START_SPEED * direction
        self.vy = random.uniform(-4, 4)

    def set_ghost(self, duration, current_time):
        """
        Activate Ghost Mode (flickering invisibility).

        Overrides Tiny mode if active.
        PowerUp persists across rounds until duration expires.

        Args:
            duration: How long ghost mode lasts (seconds)
            current_time: Current game time in seconds
        """
        self.is_ghost = True
        self.is_tiny = False
        self.modifier_end_time = current_time + duration

    def set_tiny(self, duration, current_time):
        """
        Activate Tiny Mode (half size).

        Overrides Ghost mode if active.
        PowerUp persists across rounds until duration expires.

        Args:
            duration: How long tiny mode lasts (seconds)
            current_time: Current game time in seconds
        """
        self.is_tiny = True
        self.is_ghost = False
        self.modifier_end_time = current_time + duration

    def update(self, current_time):
        """
        Update ball position, handle wall bounces, and manage modifier timers.

        Args:
            current_time: Current game time in seconds
        """
        if current_time > self.modifier_end_time:
            self.is_tiny = False
            self.is_ghost = False
            self.ghost_visible = True

        self.x += self.vx
        self.y += self.vy

        if self.y <= GAME_AREA_Y:
            self.y = GAME_AREA_Y + 1
            self.vy *= -1
        elif self.y >= GAME_AREA_Y + GAME_AREA_HEIGHT:
            self.y = GAME_AREA_Y + GAME_AREA_HEIGHT - 1
            self.vy *= -1

        if self.is_ghost:
            self.ghost_visible = (int(current_time * 6) % 2) == 0
        else:
            self.ghost_visible = True

    def get_draw_rect(self):
        """
        Return the pygame.Rect for collision detection and drawing.

        Returns:
            pygame.Rect with ball position and size
        """
        radius = BALL_RADIUS // 2 if self.is_tiny else BALL_RADIUS
        return pygame.Rect(
            int(self.x) - radius,
            int(self.y) - radius,
            radius * 2,
            radius * 2
        )
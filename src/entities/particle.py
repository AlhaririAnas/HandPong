"""
src/entities/particle.py

Simple visual effects system for collisions and celebrations.
Manages particle creation, movement, and fade-out effects.
"""

import pygame
import random


class Particle:
    """Represents a single particle for visual effects."""

    def __init__(self, x, y, color):
        """
        Initialize a particle with position and visual properties.

        Args:
            x: X position
            y: Y position
            color: RGB color tuple
        """
        self.x = x
        self.y = y

        # Random explosion velocity
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)

        self.life = 1.0  # 1.0 = 100% opacity
        self.color = color
        self.size = random.randint(2, 6)

    def update(self):
        """Update position and fade out the particle."""
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05  # Fade speed

    def draw(self, surface):
        """
        Draw the particle if it is still alive.

        Args:
            surface: Pygame surface to draw on
        """
        if self.life > 0:
            # Create temporary surface to support alpha blending (transparency)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            alpha = int(self.life * 255)

            # Draw circle onto the transparent surface
            pygame.draw.circle(
                s, (*self.color, alpha), (self.size, self.size), self.size
            )

            # Blit to main screen
            surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

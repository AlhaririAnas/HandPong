"""
src/ui/components.py

Reusable UI widgets like Buttons and Dialogs for the menu system.
"""

import pygame

from config import COLOR_SUCCESS, COLOR_DANGER


class MenuOption:
    """
    A single menu item that tracks its own selection progress (hold to select).
    """

    def __init__(self, text, number, y_pos, action_code):
        """
        Initialize a menu option.

        Args:
            text: Display text for the option
            number: Gesture number required to select (e.g., "1")
            y_pos: Y position on screen
            action_code: Action identifier when selected
        """
        self.text = text
        self.number = str(number)  # Gesture number required (e.g., "1")
        self.y_pos = y_pos
        self.action_code = action_code
        self.progress = 0.0
        self.is_selected = False

    def update(self, current_gesture, dt):
        """
        Update selection progress based on user input.

        Args:
            current_gesture: Current hand gesture (string digit or "neutral")
            dt: Delta time since last frame

        Returns:
            True if selection is confirmed (held for 1 second), False otherwise
        """
        if current_gesture == self.number:
            self.progress += dt
            self.is_selected = True
            if self.progress >= 1.0:
                self.progress = 0.0
                return True
        else:
            self.progress = 0.0
            self.is_selected = False

        return False


class ConfirmationDialog:
    """
    A modal overlay asking for Yes (1) / No (2) confirmation.
    """

    def __init__(self, text):
        """
        Initialize confirmation dialog.

        Args:
            text: Question text to display
        """
        self.text = text
        self.yes_timer = 0.0
        self.no_timer = 0.0
        self.font = pygame.font.Font(None, 60)

    def update(self, gesture, dt):
        """
        Update dialog based on gesture input.

        Args:
            gesture: Current hand gesture
            dt: Delta time since last frame

        Returns:
            'yes', 'no', or None based on gesture hold time
        """
        if gesture == "1":
            self.yes_timer += dt
            if self.yes_timer > 1.0:
                return "yes"
        elif gesture == "2":
            self.no_timer += dt
            if self.no_timer > 1.0:
                return "no"
        else:
            self.yes_timer = 0
            self.no_timer = 0

        return None

    def draw(self, surface):
        """Draw the dialog overlay with buttons and progress bars."""
        # Darkened Background
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        cx, cy = surface.get_width() // 2, surface.get_height() // 2

        # Main Question Text
        txt = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(cx, cy - 50)))

        # Draw Buttons with progress bars
        self._draw_btn(
            surface, "YES (1)", (cx - 150, cy + 50), self.yes_timer, COLOR_SUCCESS
        )
        self._draw_btn(
            surface, "NO (2)", (cx + 150, cy + 50), self.no_timer, COLOR_DANGER
        )

    def _draw_btn(self, surf, text, pos, progress, color):
        """
        Helper to draw a button with a progress bar fill.

        Args:
            surf: Pygame surface to draw on
            text: Button text
            pos: Position (x, y)
            progress: Progress value (0.0 to 1.0)
            color: RGB color tuple for the button
        """
        rect = pygame.Rect(0, 0, 200, 60)
        rect.center = pos

        # Border
        pygame.draw.rect(surf, color, rect, 2, border_radius=10)

        # Progress Fill - safely create color tuple with alpha
        if progress > 0:
            fill_w = int(200 * progress)
            fill_rect = (rect.left, rect.top, fill_w, 60)
            # Create color tuple with alpha safely
            color_with_alpha = color + (100,)
            pygame.draw.rect(surf, color_with_alpha, fill_rect, border_radius=10)

        # Button Text
        t_surf = self.font.render(text, True, color)
        surf.blit(t_surf, t_surf.get_rect(center=pos))

"""
src/ui/menu_system.py

Menu navigation logic with input safety and visual progress bars.
Handles all menu transitions and gesture-based selection with hold timers.
"""

import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MENU_TRANSITION_DELAY,
    MENU_HOLD_TIME,
    COLOR_P1,
    COLOR_TRACKING_GOOD,
    COLOR_WARNING,
)


class MenuSystem:
    """Manages menu navigation and user interaction through hand gestures."""

    def __init__(self):
        """Initialize the menu system with default state."""
        self.cx = WINDOW_WIDTH // 2
        self.cy = WINDOW_HEIGHT // 2

        # Fonts
        self.font_title = pygame.font.Font(None, 160)
        self.font_opt = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 50)

        # Menu Structures - each item has text, gesture id, and action
        self.main_menu = [
            {"text": "VS BOT", "id": "1", "action": "goto_difficulty"},
            {"text": "VS PLAYER (KEYS)", "id": "2", "action": "start_pvp"},
            {"text": "EXIT", "id": "3", "action": "confirm_exit"},
        ]

        self.diff_menu = [
            {"text": "SUPER EASY", "id": "1", "action": "super_easy"},
            {"text": "EASY", "id": "2", "action": "easy"},
            {"text": "MIDDLE", "id": "3", "action": "middle"},
            {"text": "HARD", "id": "4", "action": "hard"},
            {"text": "BACK", "id": "5", "action": "back_main"},
        ]

        self.confirm_menu = [
            {"text": "YES", "id": "1", "action": "exit_app"},
            {"text": "NO", "id": "2", "action": "back_main"},
        ]

        self.pause_menu = [
            {"text": "RESUME", "id": "1", "action": "resume"},
            {"text": "RESTART", "id": "2", "action": "restart"},
            {"text": "QUIT TO MENU", "id": "3", "action": "quit_main"},
        ]

        # State tracking
        self.selection_timer = 0.0
        self.selected_item = None
        self.ignore_timer = 0.0
        self.current_hold_limit = MENU_HOLD_TIME

    def reset_cooldown(self):
        """Prevent accidental clicks when switching screens."""
        self.ignore_timer = MENU_TRANSITION_DELAY
        self.selection_timer = 0.0
        self.selected_item = None

    def update(self, current_list, gesture, dt, hold_time=MENU_HOLD_TIME):
        """
        Update menu selection based on hand gesture.

        Args:
            current_list: List of menu items to navigate
            gesture: Current hand gesture (string digit or "neutral")
            dt: Delta time since last frame
            hold_time: Time to hold gesture for selection (seconds)

        Returns:
            Action string if selection confirmed, None otherwise
        """
        self.current_hold_limit = hold_time

        # 1. Safety Cooldown - ignore input for transition delay
        if self.ignore_timer > 0:
            self.ignore_timer -= dt
            return None

        # 2. Map Gesture to Menu Item
        target = None
        if gesture and gesture.isdigit():
            for item in current_list:
                if item["id"] == gesture:
                    target = item
                    break

        # 3. Selection Hold Logic
        if target:
            if self.selected_item == target:
                self.selection_timer += dt
                if self.selection_timer >= hold_time:
                    # Action Confirmed
                    self.selection_timer = 0.0
                    self.selected_item = None
                    self.ignore_timer = MENU_TRANSITION_DELAY
                    return target["action"]
            else:
                # New item selected, start timer
                self.selected_item = target
                self.selection_timer = 0.0
        else:
            # Gesture lost
            self.selected_item = None
            self.selection_timer = 0.0

        return None

    def draw(self, surface, title, menu_list, overlay=False):
        """
        Draw the menu with progress bar under selected item.

        Args:
            surface: Pygame surface to draw on
            title: Menu title text
            menu_list: List of menu items to display
            overlay: If True, draw semi-transparent background
        """
        if overlay:
            # Draw semi-transparent background
            bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            bg.set_alpha(220)
            bg.fill((5, 5, 10))
            surface.blit(bg, (0, 0))
        else:
            # Solid background
            surface.fill((10, 10, 10))

        # Title
        t_surf = self.font_title.render(title, True, (255, 255, 255))
        surface.blit(t_surf, t_surf.get_rect(center=(self.cx, 250)))

        start_y = 450
        gap = 120  # Increased gap for load-line space

        for i, item in enumerate(menu_list):
            y_pos = start_y + (i * gap)
            is_sel = self.selected_item == item

            # Determine color (Dim if handling cooldown)
            if self.ignore_timer > 0:
                color = (60, 60, 60)
            else:
                color = COLOR_P1 if not is_sel else COLOR_TRACKING_GOOD

            # Draw Selection Box
            box_width = 600
            box_height = 80

            if is_sel and self.ignore_timer <= 0:
                # Highlight Box
                pygame.draw.rect(
                    surface,
                    (0, 50, 0),
                    (
                        self.cx - box_width // 2,
                        y_pos - box_height // 2,
                        box_width,
                        box_height,
                    ),
                    border_radius=15,
                )
                pygame.draw.rect(
                    surface,
                    color,
                    (
                        self.cx - box_width // 2,
                        y_pos - box_height // 2,
                        box_width,
                        box_height,
                    ),
                    2,
                    border_radius=15,
                )

                # --- LOAD LINE (Progress Bar) ---
                bar_y = y_pos + box_height // 2 + 10
                pygame.draw.rect(
                    surface,
                    (40, 40, 40),
                    (self.cx - box_width // 2, bar_y, box_width, 8),
                    border_radius=4,
                )

                # Fill Bar (Green/Color)
                if self.current_hold_limit > 0:
                    progress = min(1.0, self.selection_timer / self.current_hold_limit)
                    fill_width = int(box_width * progress)
                    pygame.draw.rect(
                        surface,
                        color,
                        (self.cx - box_width // 2, bar_y, fill_width, 8),
                        border_radius=4,
                    )

            # Draw Text
            txt = f"{item['id']} {item['text']}"
            r = self.font_opt.render(txt, True, color)
            rect = r.get_rect(center=(self.cx, y_pos))
            surface.blit(r, rect)

        # Footer Status
        if self.ignore_timer > 0:
            h = self.font_small.render("LOADING INPUT...", True, COLOR_WARNING)
        else:
            h = self.font_small.render(
                "HOLD FINGER NUMBER TO SELECT", True, (80, 80, 80)
            )
        surface.blit(h, h.get_rect(center=(self.cx, WINDOW_HEIGHT - 80)))

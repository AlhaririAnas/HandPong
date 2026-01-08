"""
ui_menu.py - Pong Game v5.0
Menu rendering and navigation
"""

import pygame
from config import (
    COLOR_FOREGROUND, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SEPARATOR,
    COLOR_BACKGROUND, COLOR_CONFIRM_BG, COLOR_SUCCESS, COLOR_DANGER,
    FONT_SIZE_MENU_TITLE, FONT_SIZE_MENU_OPTION, FONT_SIZE_MENU_SMALL,
    FONT_SIZE_CONFIRM,
    MENU_CENTER_X, MENU_CENTER_Y, MENU_OPTION_SPACING
)

class MenuRenderer:
    """Renders menu screens and confirmation overlays."""
    
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.font_title = pygame.font.Font(None, FONT_SIZE_MENU_TITLE)
        self.font_option = pygame.font.Font(None, FONT_SIZE_MENU_OPTION)
        self.font_small = pygame.font.Font(None, FONT_SIZE_MENU_SMALL)
        self.font_confirm = pygame.font.Font(None, FONT_SIZE_CONFIRM)
    
    def draw_main_menu(self, selected_index: int):
        self._draw_generic_menu(
            "PONG", 
            ["[1] NEW GAME", "[2] EXIT"], 
            selected_index, 
            -50
        )
    
    def draw_difficulty_menu(self, selected_index: int):
        self._draw_generic_menu(
            "SELECT MODE", 
            ["[1] vs BOT", "[2] vs PLAYER", "[3] BACK"], 
            selected_index, 
            -50
        )
    
    def draw_bot_difficulty_menu(self, selected_index: int):
        options = [
            "[1] SUPER EASY", 
            "[2] EASY", 
            "[3] MIDDLE", 
            "[4] HARD", 
            "[5] BACK"
        ]
        self._draw_generic_menu(
            "DIFFICULTY", 
            options, 
            selected_index, 
            -150
        )

    def _draw_generic_menu(self, title_text, options, selected_index, offset_y):
        self.surface.fill(COLOR_BACKGROUND)
        
        # Title
        title = self.font_title.render(title_text, True, COLOR_FOREGROUND)
        self.surface.blit(title, title.get_rect(center=(MENU_CENTER_X, 200)))
        
        # Options
        start_y = MENU_CENTER_Y + offset_y
        for i, text_str in enumerate(options):
            y = start_y + i * MENU_OPTION_SPACING
            text = self.font_option.render(text_str, True, COLOR_TEXT)
            rect = text.get_rect(center=(MENU_CENTER_X, y))
            
            # Highlight selected
            padding = 20
            border_rect = rect.inflate(padding * 4, padding * 2)
            if i == selected_index:
                pygame.draw.rect(self.surface, COLOR_FOREGROUND, border_rect, 4)
                s = pygame.Surface(border_rect.size)
                s.set_alpha(30)
                s.fill(COLOR_FOREGROUND)
                self.surface.blit(s, border_rect.topleft)
            else:
                pygame.draw.rect(self.surface, COLOR_SEPARATOR, border_rect, 2)
            
            self.surface.blit(text, rect)
            
        # Hints
        hint = self.font_small.render("SHOW FINGER NUMBER TO SELECT", True, COLOR_TEXT_DIM)
        self.surface.blit(hint, hint.get_rect(center=(MENU_CENTER_X, 950)))

    def draw_confirmation_dialog(self, option_name: str):
        """Draws an overlay asking for confirmation."""
        # 1. Darken background
        overlay = pygame.Surface(self.surface.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.surface.blit(overlay, (0, 0))
        
        # 2. Box
        box_width, box_height = 800, 500
        box_rect = pygame.Rect(0, 0, box_width, box_height)
        box_rect.center = (MENU_CENTER_X, MENU_CENTER_Y)
        pygame.draw.rect(self.surface, COLOR_CONFIRM_BG, box_rect, 0, 20)
        pygame.draw.rect(self.surface, COLOR_FOREGROUND, box_rect, 4, 20)
        
        # 3. Text
        title = self.font_confirm.render(f"SELECT {option_name}?", True, COLOR_TEXT)
        self.surface.blit(title, title.get_rect(center=(MENU_CENTER_X, MENU_CENTER_Y - 100)))
        
        # 4. Instructions (Thumbs Up/Down)
        yes_text = self.font_option.render("THUMBS UP: YES", True, COLOR_SUCCESS)
        no_text = self.font_option.render("THUMBS DOWN: NO", True, COLOR_DANGER)
        
        self.surface.blit(yes_text, yes_text.get_rect(center=(MENU_CENTER_X, MENU_CENTER_Y + 50)))
        self.surface.blit(no_text, no_text.get_rect(center=(MENU_CENTER_X, MENU_CENTER_Y + 130)))
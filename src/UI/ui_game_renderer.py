"""
ui_game_renderer.py - Pong Game v5.0
Game Rendering (NO Logic)
"""

import pygame
from config import (
    COLOR_FOREGROUND, COLOR_ACCENT, COLOR_TEXT, COLOR_BACKGROUND,
    COLOR_SEPARATOR, COLOR_BALL,
    FONT_SIZE_SCORE, FONT_SIZE_GAMEOVER, FONT_SIZE_DIFFICULTY,
    GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT,
    SCORE_LEFT_X, SCORE_RIGHT_X, SCORE_Y, LEVEL_X, LEVEL_Y,
    SCORE_BG_ALPHA, MENU_CENTER_X, MENU_CENTER_Y,
    PADDLE_HEIGHT, PADDLE_WIDTH, BALL_SIZE, MAX_SCORE
)


class GameRenderer:
    """Renders game state."""
    
    def __init__(self, surface: pygame.Surface):
        """Initialize game renderer."""
        self.surface = surface
        self.font_score = pygame.font.Font(None, FONT_SIZE_SCORE)
        self.font_level = pygame.font.Font(None, FONT_SIZE_DIFFICULTY)
        self.font_gameover = pygame.font.Font(None, FONT_SIZE_GAMEOVER)
    
    def draw_game(self, game):
        """Draw complete game."""
        self.surface.fill(COLOR_BACKGROUND)
        
        self._draw_game_area()
        self._draw_paddles(game)
        self._draw_ball(game)
        self._draw_scores(game)
        self._draw_level(game)
    
    def draw_game_over(self, game):
        """Draw game over screen."""
        # Draw game background first
        self.draw_game(game)
        
        # Determine winner
        player1_won = game.player_score >= MAX_SCORE
        winner_text = "YOU WIN!" if player1_won else "YOU LOSE!"
        winner_color = COLOR_FOREGROUND if player1_won else COLOR_ACCENT
        
        # Position: left side for player 1, right side for opponent
        if player1_won:
            # Player 1 won: show on left side
            win_x = GAME_AREA_X + GAME_AREA_WIDTH * 0.25
        else:
            # Player 2 won: show on right side
            win_x = GAME_AREA_X + GAME_AREA_WIDTH * 0.75
        
        win_y = MENU_CENTER_Y - 100
        
        game_over_text = self.font_gameover.render(winner_text, True, winner_color)
        text_rect = game_over_text.get_rect(center=(win_x, win_y))
        
        # Semi-transparent background
        s = pygame.Surface((800, 200))
        s.set_alpha(180)
        s.fill(COLOR_BACKGROUND)
        self.surface.blit(s, text_rect.inflate(100, 100).topleft)
        self.surface.blit(game_over_text, text_rect)
        
        # Continue Hint
        font_small = pygame.font.Font(None, 50)
        continue_text = font_small.render("Press SPACE to continue", True, COLOR_TEXT)
        continue_rect = continue_text.get_rect(center=(MENU_CENTER_X, win_y + 150))
        self.surface.blit(continue_text, continue_rect)
    
    def _draw_game_area(self):
        """Draw game area border + center line."""
        # Border
        pygame.draw.rect(
            self.surface,
            COLOR_FOREGROUND,
            (GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT),
            3
        )
        
        # Center Line
        for y in range(GAME_AREA_Y, GAME_AREA_Y + GAME_AREA_HEIGHT, 30):
            pygame.draw.line(
                self.surface,
                COLOR_SEPARATOR,
                (GAME_AREA_X + GAME_AREA_WIDTH // 2, y),
                (GAME_AREA_X + GAME_AREA_WIDTH // 2, y + 15),
                2
            )
    
    def _draw_paddles(self, game):
        """Draw both paddles."""
        # Left Paddle (Player 1) - Cyan
        pygame.draw.rect(
            self.surface,
            COLOR_FOREGROUND,
            (GAME_AREA_X, game.player_paddle_y, 
             PADDLE_WIDTH, PADDLE_HEIGHT),
            3
        )
        
        # Right Paddle (Player 2 / AI) - Magenta
        right_paddle_y = game.ai_paddle_y if game.game_mode == 'bot' else game.player2_paddle_y
        pygame.draw.rect(
            self.surface,
            COLOR_ACCENT,
            (GAME_AREA_X + GAME_AREA_WIDTH - PADDLE_WIDTH, 
             right_paddle_y,
             PADDLE_WIDTH, PADDLE_HEIGHT),
            3
        )
    
    def _draw_ball(self, game):
        """Draw the ball."""
        # Only draw if ball is active (not beyond boundaries)
        if game.ball_active:
            # Check if ball is within play area bounds
            if (GAME_AREA_X <= game.ball_x <= GAME_AREA_X + GAME_AREA_WIDTH and
                GAME_AREA_Y <= game.ball_y <= GAME_AREA_Y + GAME_AREA_HEIGHT):
                
                pygame.draw.circle(
                    self.surface,
                    COLOR_BALL,
                    (int(game.ball_x), int(game.ball_y)),
                    int(BALL_SIZE / 2)
                )
    
    def _draw_scores(self, game):
        """Draw scores INSIDE game area."""
        # Left Score (Player 1)
        player_text = self.font_score.render(str(game.player_score), True, COLOR_FOREGROUND)
        player_rect = player_text.get_rect(center=(int(SCORE_LEFT_X), int(SCORE_Y)))
        
        # Semi-transparent background
        s = pygame.Surface((150, 100))
        s.set_alpha(int(255 * SCORE_BG_ALPHA))
        s.fill(COLOR_BACKGROUND)
        self.surface.blit(s, player_rect.topleft)
        self.surface.blit(player_text, player_rect)
        
        # Right Score (Player 2 / AI)
        ai_text = self.font_score.render(str(game.ai_score), True, COLOR_ACCENT)
        ai_rect = ai_text.get_rect(center=(int(SCORE_RIGHT_X), int(SCORE_Y)))
        
        s = pygame.Surface((150, 100))
        s.set_alpha(int(255 * SCORE_BG_ALPHA))
        s.fill(COLOR_BACKGROUND)
        self.surface.blit(s, ai_rect.topleft)
        self.surface.blit(ai_text, ai_rect)
    
    def _draw_level(self, game):
        """Draw level OUTSIDE game area."""
        level_text = self.font_level.render(
            f"LEVEL {game.current_level}", 
            True, COLOR_TEXT
        )
        level_rect = level_text.get_rect(center=(int(LEVEL_X), int(LEVEL_Y)))
        self.surface.blit(level_text, level_rect)
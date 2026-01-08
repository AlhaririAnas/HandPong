"""
src/ui/renderer.py

Handles all visual rendering including game field, entities, HUD, and overlays.
Manages font rendering, particle effects, and UI elements.
"""

import pygame
import math
import time

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GAME_AREA_X, GAME_AREA_Y,
    GAME_AREA_WIDTH, GAME_AREA_HEIGHT, COLOR_BG, COLOR_GRID,
    COLOR_UI_TEXT, COLOR_UI_GHOST, COLOR_P1, COLOR_P2
)


class Renderer:
    """Handles all visual rendering for the game."""

    def __init__(self, surface):
        """
        Initialize the renderer with pygame surface.

        Args:
            surface: Pygame surface to render to
        """
        self.surface = surface

        self.font_score = pygame.font.Font(None, 300)
        self.font_info = pygame.font.Font(None, 40)
        self.font_power = pygame.font.Font(None, 50)
        self.font_math = pygame.font.Font(None, 70)
        self.font_overlay = pygame.font.Font(None, 100)
        self.font_menu = pygame.font.Font(None, 60)

    def draw_game(self, engine):
        """
        Main rendering loop for active game.

        Args:
            engine: GameEngine instance with current state
        """
        self.surface.fill(COLOR_BG)

        self._draw_field_background()

        midx = GAME_AREA_X + GAME_AREA_WIDTH // 2
        self._draw_bg_score(engine.player.score, midx - 300, COLOR_P1)
        self._draw_bg_score(engine.ai.score, midx + 300, COLOR_P2)

        self._draw_hud(engine, midx)

        if engine.player.has_agility:
            self._draw_agility_trail(engine.player)
        if engine.ai.has_agility:
            self._draw_agility_trail(engine.ai)

        self._draw_paddle(engine.player)
        self._draw_paddle(engine.ai)
        self._draw_ball(engine.ball)

        for p in engine.particles:
            p.draw(self.surface)

        if engine.player.active_powerup_text:
            self._draw_powerup_text(
                engine.player.active_powerup_text,
                midx - 300,
                COLOR_P1
            )
        if engine.ai.active_powerup_text:
            self._draw_powerup_text(
                engine.ai.active_powerup_text,
                midx + 300,
                COLOR_P2
            )

        if engine.math_sys.active:
            self._draw_math_task(engine.math_sys)

        if engine.state == "game_over":
            self._draw_overlay(engine.winner_text, "PRESS 5 TO RESTART")

    def _draw_field_background(self):
        """Draw the game field with borders and center line."""
        r = pygame.Rect(
            GAME_AREA_X,
            GAME_AREA_Y,
            GAME_AREA_WIDTH,
            GAME_AREA_HEIGHT
        )
        pygame.draw.rect(self.surface, (12, 12, 18), r)
        pygame.draw.rect(self.surface, COLOR_GRID, r, 2)

        mx = GAME_AREA_X + GAME_AREA_WIDTH // 2
        pygame.draw.line(
            self.surface,
            COLOR_GRID,
            (mx, GAME_AREA_Y),
            (mx, GAME_AREA_Y + GAME_AREA_HEIGHT),
            2
        )

    def _draw_bg_score(self, score, x, color):
        """
        Draw large semi-transparent score number in background.

        Args:
            score: Score value to display
            x: X position (centered)
            color: RGB color tuple
        """
        s = self.font_score.render(str(score), True, color)
        s.set_alpha(50)
        self.surface.blit(s, s.get_rect(center=(x, GAME_AREA_Y + GAME_AREA_HEIGHT // 2)))

    def _draw_hud(self, engine, midx):
        """
        Draw HUD info including level and time.

        Args:
            engine: GameEngine instance
            midx: X center position
        """
        txt = f"LEVEL {engine.level} | TIME {engine.game_time_str}"
        surf = self.font_info.render(txt, True, COLOR_UI_GHOST)
        self.surface.blit(
            surf,
            surf.get_rect(center=(midx, GAME_AREA_Y + GAME_AREA_HEIGHT - 30))
        )

    def _draw_agility_trail(self, paddle):
        """
        Draw ghost copies of paddle for Agility visual effect.

        Args:
            paddle: Paddle instance with trail history
        """
        for i, rect in enumerate(paddle.trail_history):
            progress = i / len(paddle.trail_history)
            alpha = int(150 * progress)

            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*paddle.color, alpha), s.get_rect(), border_radius=8)
            self.surface.blit(s, rect.topleft)

    def _draw_paddle(self, paddle):
        """
        Draw paddle with appropriate visual effect.

        Args:
            paddle: Paddle instance
        """
        if paddle.is_trampoline:
            rect = paddle.rect
            midscreen = GAME_AREA_X + GAME_AREA_WIDTH // 2
            is_left_side = rect.centerx < midscreen

            if is_left_side:
                start_angle = -math.pi / 2
                end_angle = math.pi / 2
            else:
                start_angle = math.pi / 2
                end_angle = 3 * math.pi / 2

            arc_rect = rect.inflate(25, 0)
            pygame.draw.arc(
                self.surface,
                (200, 255, 255),
                arc_rect.inflate(10, 10),
                start_angle,
                end_angle,
                8
            )
            pygame.draw.arc(
                self.surface,
                paddle.color,
                arc_rect,
                start_angle,
                end_angle,
                6
            )
            pygame.draw.rect(
                self.surface,
                paddle.color,
                rect.inflate(-10, 0),
                border_radius=4
            )
        else:
            if paddle.active_powerup_text:
                glow = pygame.Surface(
                    (paddle.rect.width + 30, paddle.rect.height + 30),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    glow,
                    (*paddle.color, 60),
                    glow.get_rect(),
                    border_radius=15
                )
                self.surface.blit(glow, (paddle.rect.x - 15, paddle.rect.y - 15))

            pygame.draw.rect(
                self.surface,
                paddle.color,
                paddle.rect,
                border_radius=8
            )

    def _draw_ball(self, ball):
        """
        Draw ball with visual modifiers (Ghost, Tiny).

        Args:
            ball: Ball instance
        """
        if not ball.ghost_visible:
            return

        if ball.is_tiny:
            col = (255, 50, 50)
        else:
            col = (255, 255, 255)

        if ball.is_ghost:
            col = (100, 255, 100)

        rect = ball.get_draw_rect()
        pygame.draw.circle(
            self.surface,
            col,
            (int(ball.x), int(ball.y)),
            rect.width // 2
        )

    def _draw_math_task(self, math_sys):
        """
        Draw math task overlay with progress bar.

        Args:
            math_sys: MathSystem instance
        """
        mx = GAME_AREA_X + GAME_AREA_WIDTH // 2
        ypos = GAME_AREA_Y + 80

        rect = pygame.Rect(0, 0, 300, 70)
        rect.center = (mx, ypos)

        pygame.draw.rect(self.surface, (30, 30, 40), rect, border_radius=20)
        pygame.draw.rect(self.surface, (255, 215, 0), rect, 2, border_radius=20)

        txt = self.font_math.render(
            f"{math_sys.equation_string} = ?",
            True,
            (255, 255, 255)
        )
        self.surface.blit(txt, txt.get_rect(center=rect.center))

        progress = math_sys.get_progress(time.time())
        barw = int(280 * (1.0 - progress))
        if barw > 0:
            col = (
                int(255 * progress),
                int(255 * (1 - progress)),
                0
            )
            pygame.draw.rect(
                self.surface,
                col,
                (rect.left - 10, rect.bottom + 10, barw, 4)
            )

    def _draw_powerup_text(self, text, x, color):
        """
        Draw powerup status text for paddle.

        Only displayed while powerup is active (active_powerup_text is not None).

        Args:
            text: Powerup name to display
            x: X position (centered)
            color: RGB color tuple
        """
        t = self.font_power.render(text, True, color)
        self.surface.blit(
            t,
            t.get_rect(center=(x, GAME_AREA_Y + 40))
        )

    def _draw_overlay(self, title, subtitle):
        """
        Draw full-screen overlay with title and subtitle.

        Args:
            title: Main title text
            subtitle: Subtitle text
        """
        o = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        o.set_alpha(230)
        o.fill((10, 10, 15))
        self.surface.blit(o, (0, 0))

        t1 = self.font_overlay.render(title, True, (255, 255, 255))
        self.surface.blit(
            t1,
            t1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        )

        t2 = self.font_info.render(subtitle, True, COLOR_UI_GHOST)
        self.surface.blit(
            t2,
            t2.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        )
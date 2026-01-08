"""
src/core/game_engine.py

Central logic hub coordinating entities, physics, collisions, and game rules.
Manages paddle movement, ball physics, powerups, and AI logic.
"""

import pygame
import random
import time
import math

from config import *
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.entities.particle import Particle
from src.core.math_system import MathSystem
from src.core.utils import map_angle_to_paddle_y


class GameEngine:
    """Central game logic coordinator."""

    def __init__(self):
        """Initialize the game engine with default state."""
        self.state = "menu"
        self.game_mode = "bot"

        self.player = Paddle(GAME_AREA_X + 30, is_ai=False)
        self.ai = Paddle(GAME_AREA_X + GAME_AREA_WIDTH - 30 - PADDLE_WIDTH, is_ai=True)
        self.ball = Ball()
        self.particles = []
        self.math_sys = MathSystem()

        self.level = 1
        self.start_time = 0
        self.game_time_str = "00:00"
        self.winner_text = ""
        self.last_math_time = 0
        self.time_limit = TIME_LIMIT
        self.sudden_death = False
        self.total_hits = 0
        self.ball_current_base_speed = BALL_START_SPEED

    def start_game(self, mode="bot", difficulty="middle"):
        """
        Initialize a new game session.

        Args:
            mode: Game mode ("bot" or "pvp")
            difficulty: AI difficulty level ("super_easy", "easy", "middle", "hard")
        """
        self.game_mode = mode
        self.player.reset()
        self.ai.reset()

        self.ball_current_base_speed = BALL_START_SPEED
        self._reset_ball_with_speed()

        self.particles.clear()
        self.math_sys.reset()

        self.ai.is_ai = (self.game_mode != "pvp")

        self.level = 1
        self.total_hits = 0
        self.start_time = time.time()
        self.last_math_time = time.time()
        self.sudden_death = False
        self.state = "playing"

    def update(self, hand_data, dt):
        """
        Main game loop tick.

        Args:
            hand_data: Dictionary containing hand tracking data
            dt: Delta time since last frame
        """
        if self.state != "playing":
            return

        curr_time = time.time()
        self._update_time_and_check_win(curr_time)

        if self.state != "playing":
            return

        if hand_data.get('pause_progress', 0) >= 1.0:
            self.state = "paused"
            return

        target_y_rel = map_angle_to_paddle_y(
            hand_data['angle'],
            GAME_AREA_HEIGHT,
            self.player.rect.height,
            PADDLE_ANGLE_UP, PADDLE_ANGLE_DOWN
        )
        self.player.move(GAME_AREA_Y + target_y_rel)

        if self.game_mode == "pvp":
            self._update_local_pvp(dt)
        else:
            self._update_ai(dt)

        self.player.update(curr_time)
        self.ai.update(curr_time)
        self.ball.update(curr_time)

        self._handle_collisions()
        self._check_score()
        self._manage_math_tasks(curr_time, hand_data.get('gesture'))

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def _reset_ball_with_speed(self):
        """Reset ball to center with current speed settings."""
        self.ball.reset()
        dir_x = random.choice([-1, 1])
        dir_y = random.uniform(-0.5, 0.5)
        self.ball.vx = self.ball_current_base_speed * dir_x
        self.ball.vy = self.ball_current_base_speed * dir_y

    def _update_time_and_check_win(self, curr_time):
        """
        Update game time display and check for game over condition.

        Args:
            curr_time: Current game time in seconds
        """
        elapsed = curr_time - self.start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        self.game_time_str = f"{mins:02}:{secs:02}"

        if elapsed >= self.time_limit:
            if self.player.score != self.ai.score:
                self.state = "game_over"
                self.winner_text = (
                    "PLAYER 1 WINS"
                    if self.player.score > self.ai.score
                    else "PLAYER 2 WINS"
                )
            else:
                self.sudden_death = True
                self.game_time_str = "SUDDEN DEATH"

    def _update_local_pvp(self, dt):
        """
        Update Player 2 position using keyboard control.

        Args:
            dt: Delta time since last frame
        """
        keys = pygame.key.get_pressed()
        move_y = 0

        if keys[pygame.K_UP]:
            move_y = -KEYBOARD_SPEED * dt
        elif keys[pygame.K_DOWN]:
            move_y = KEYBOARD_SPEED * dt

        if move_y != 0:
            self.ai.move(self.ai.rect.y + move_y)

    def _update_ai(self, dt):
        """
        Simple AI tracking logic for bot opponent.

        Args:
            dt: Delta time since last frame
        """
        target = self.ball.y - self.ai.rect.height // 2

        if self.ball.is_ghost and not self.ball.ghost_visible:
            pass
        else:
            self.ai.move(target)

    def _handle_collisions(self):
        """Check Ball vs Paddle collisions and apply physics."""
        b_rect = self.ball.get_draw_rect()

        if b_rect.colliderect(self.player.rect) and self.ball.vx < 0:
            self._reflect_ball(self.player, 1)
            self._spawn_collision_particles(
                self.player.rect.right,
                self.ball.y,
                self.player.color
            )

        elif b_rect.colliderect(self.ai.rect) and self.ball.vx > 0:
            self._reflect_ball(self.ai, -1)
            self._spawn_collision_particles(
                self.ai.rect.left,
                self.ball.y,
                self.ai.color
            )

    def _reflect_ball(self, paddle, direction):
        """
        Handle physics and game progression on paddle hit.

        Args:
            paddle: Paddle instance that hit the ball
            direction: Direction multiplier (1 for left, -1 for right)
        """
        self.total_hits += 1

        if self.total_hits % HITS_PER_LEVEL == 0:
            self.level += 1
            self.ball_current_base_speed = min(
                self.ball_current_base_speed + SPEED_INCREMENT_PER_LEVEL,
                BALL_MAX_SPEED
            )

        current_speed = self.ball_current_base_speed

        if paddle.is_trampoline:
            current_speed *= 1.7
            self._spawn_trampoline_effect(paddle)
            current_speed = min(current_speed, BALL_MAX_SPEED)

        offset = (self.ball.y - paddle.rect.centery) / (paddle.rect.height / 2)
        bounce_angle = offset * 50

        rad = math.radians(bounce_angle)
        self.ball.vx = current_speed * math.cos(rad) * direction
        self.ball.vy = current_speed * math.sin(rad)

        if direction == 1 and self.ball.vx < 0:
            self.ball.vx *= -1
        if direction == -1 and self.ball.vx > 0:
            self.ball.vx *= -1

    def _manage_math_tasks(self, curr_time, gesture):
        """
        Generate math tasks and check answers from gestures or keyboard.

        Args:
            curr_time: Current game time in seconds
            gesture: Hand gesture detected (string digit "0"-"5" or None)
        """
        if not self.math_sys.active:
            if curr_time - self.last_math_time > MATH_TASK_INTERVAL:
                if self.math_sys.generate_task(curr_time):
                    self.last_math_time = curr_time
        else:
            if gesture and gesture.isdigit():
                if self.math_sys.check_answer(int(gesture)):
                    self._resolve_math(curr_time, winner="player")
                    return

            if self.game_mode == "pvp":
                keys = pygame.key.get_pressed()
                key_map = {
                    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                    pygame.K_4: 4, pygame.K_5: 5, pygame.K_0: 0
                }
                for k, val in key_map.items():
                    if keys[k] and self.math_sys.check_answer(val):
                        self._resolve_math(curr_time, winner="opponent")
                        return

            if self.math_sys.get_time_left(curr_time) <= 0:
                if self.game_mode == "pvp":
                    self.math_sys.active = False
                else:
                    self._resolve_math(curr_time, winner="bot")

    def _resolve_math(self, t, winner):
        """
        Award powerups to the winner of the math task.

        Args:
            t: Current game time in seconds
            winner: "player", "opponent" (PvP), or "bot"
        """
        self.math_sys.active = False

        if winner == "player":
            self._spawn_fireworks(GAME_AREA_X + GAME_AREA_WIDTH // 4)
            roster = [
                ("enlarge", "ENLARGE", self.player),
                ("trampoline", "TRAMPOLINE", self.player),
                ("agility", "AGILITY", self.player),
                ("shrink", "SHRINK", self.ai),
                ("tiny", "TINY BALL", None),
                ("ghost", "GHOST BALL", None)
            ]
            eff, name, entity = random.choice(roster)
            self._apply_effect(eff, name, entity, t, winner_obj=self.player)

        elif winner == "opponent":
            self._spawn_fireworks(GAME_AREA_X + 3 * GAME_AREA_WIDTH // 4)
            roster = [
                ("enlarge", "ENLARGE", self.ai),
                ("trampoline", "TRAMPOLINE", self.ai),
                ("agility", "AGILITY", self.ai),
                ("shrink", "SHRINK", self.player),
                ("tiny", "TINY BALL", None),
                ("ghost", "GHOST BALL", None)
            ]
            eff, name, entity = random.choice(roster)
            self._apply_effect(eff, name, entity, t, winner_obj=self.ai)

        else:
            self._spawn_fireworks(GAME_AREA_X + 3 * GAME_AREA_WIDTH // 4)
            roster = [
                ("enlarge", "ENLARGE", self.ai),
                ("trampoline", "TRAMPOLINE", self.ai),
                ("agility", "AGILITY", self.ai),
                ("shrink", "SHRINK", self.player),
                ("tiny", "TINY BALL", None),
                ("ghost", "GHOST BALL", None)
            ]
            eff, name, entity = random.choice(roster)
            self._apply_effect(eff, name, entity, t, winner_obj=self.ai)

    def _apply_effect(self, eff, name, entity, t, winner_obj=None):
        """
        Apply the selected powerup effect.

        Args:
            eff: Effect type ("enlarge", "shrink", "trampoline", "agility", "tiny", "ghost")
            name: Display name of the powerup
            entity: Paddle entity to apply effect to (or None for ball effects)
            t: Current game time in seconds
            winner_obj: Paddle that won (used for ball powerup text display)
        """
        if eff == "tiny":
            self.ball.set_tiny(POWERUP_DURATION, t)
            if winner_obj:
                winner_obj.active_powerup_text = name
                winner_obj.powerup_end_time = t + POWERUP_DURATION
        elif eff == "ghost":
            self.ball.set_ghost(POWERUP_DURATION, t)
            if winner_obj:
                winner_obj.active_powerup_text = name
                winner_obj.powerup_end_time = t + POWERUP_DURATION
        else:
            entity.apply_powerup(eff, name, POWERUP_DURATION, t)

    def _spawn_collision_particles(self, x, y, color):
        """
        Spawn particle burst at collision point.

        Args:
            x: X coordinate of collision
            y: Y coordinate of collision
            color: RGB color tuple for particles
        """
        for _ in range(8):
            self.particles.append(Particle(x, y, color))

    def _spawn_trampoline_effect(self, paddle):
        """
        Spawn particles for trampoline visual effect.

        Args:
            paddle: Paddle with trampoline effect
        """
        for _ in range(12):
            self.particles.append(
                Particle(paddle.rect.centerx, paddle.rect.centery, paddle.color)
            )

    def _spawn_fireworks(self, x_pos):
        """
        Spawn fireworks at position.

        Args:
            x_pos: X coordinate for fireworks center
        """
        y_pos = GAME_AREA_Y + GAME_AREA_HEIGHT // 2
        for _ in range(40):
            p = Particle(x_pos, y_pos, (255, 215, 0))
            p.vx *= 3
            p.vy *= 3
            p.size = random.randint(4, 9)
            self.particles.append(p)

    def _check_score(self):
        """Detect if ball is out of bounds and update score."""
        if self.ball.x < GAME_AREA_X - 20:
            self.ai.score += 1
            self._reset_ball_with_speed()
            if self.sudden_death:
                self._end_sudden_death("PLAYER 2")
        elif self.ball.x > GAME_AREA_X + GAME_AREA_WIDTH + 20:
            self.player.score += 1
            self._reset_ball_with_speed()
            if self.sudden_death:
                self._end_sudden_death("PLAYER 1")

        if self.player.score >= WIN_SCORE or self.ai.score >= WIN_SCORE:
            self.state = "game_over"
            self.winner_text = (
                "PLAYER 1 WINS"
                if self.player.score > self.ai.score
                else "PLAYER 2 WINS"
            )

    def _end_sudden_death(self, winner_name):
        """
        End sudden death mode and declare winner.

        Args:
            winner_name: Name of the winning player
        """
        self.state = "game_over"
        self.winner_text = f"{winner_name} WINS"
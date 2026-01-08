"""
main.py

Main entry point for the Hand Pong application.
Handles command-line arguments to switch between game and data recorder modes.
"""

import sys
import argparse
import logging
import pygame
import cv2

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    GAME_TITLE,
    FPS,
    GAME_AREA_X,
    GAME_AREA_Y,
    GAME_AREA_WIDTH,
    GAME_AREA_HEIGHT,
    PAUSE_SELECTION_TIME,
)

from src.core.game_engine import GameEngine
from src.input.hand_controller import HandController
from src.ui.renderer import Renderer
from src.ui.menu_system import MenuSystem
from src.ui.camera_view import draw_camera_pip

from analysis.data_recorder import DataRecorder


def setup_logging():
    """Configure logging format for the application."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def run_game_loop():
    """
    Initialize and run the main game loop.

    This includes the menu system, game engine updates, and rendering.
    """
    logging.info("Initializing game modules...")

    # Pygame setup
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    # Core modules
    engine = GameEngine()
    input_ctrl = HandController()
    renderer = Renderer(screen)
    menu = MenuSystem()

    # Camera setup
    logging.info("Starting camera input...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logging.error("Could not open camera. Please check your device.")
        sys.exit(1)

    running = True
    logging.info("Game started. Press 'Q' to quit.")

    while running:
        # Calculate delta time in seconds
        dt = clock.tick(FPS) / 1000.0

        # Handle Pygame events (Window close, Keyboard shortcuts)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # 1. Process Camera Input
        ret, frame = cap.read()
        hand_data = {}

        if ret:
            # Flip the frame for a more natural mirror view
            frame = cv2.flip(frame, 1)

            # Process hand gestures and angles
            hand_data = input_ctrl.process(frame, dt)

        # 2. Update Game State
        current_state = engine.state

        # --- MENU STATE ---
        if current_state == "menu":
            action = menu.update(menu.main_menu, hand_data.get("gesture"), dt)

            if action == "goto_difficulty":
                engine.state = "difficulty_select"
                menu.reset_cooldown()
            elif action == "start_pvp":
                engine.start_game(mode="pvp")
            elif action == "confirm_exit":
                engine.state = "confirm_exit"
                menu.reset_cooldown()

            menu.draw(screen, GAME_TITLE, menu.main_menu)

        # --- DIFFICULTY SELECTION ---
        elif current_state == "difficulty_select":
            action = menu.update(menu.diff_menu, hand_data.get("gesture"), dt)

            if action == "back_main":
                engine.state = "menu"
                menu.reset_cooldown()
            elif action in ["super_easy", "easy", "middle", "hard"]:
                # Start the game with the selected bot difficulty
                engine.start_game(mode="bot", difficulty=action)

            menu.draw(screen, "SELECT DIFFICULTY", menu.diff_menu)

        # --- EXIT CONFIRMATION ---
        elif current_state == "confirm_exit":
            action = menu.update(menu.confirm_menu, hand_data.get("gesture"), dt)

            if action == "exit_app":
                running = False
            elif action == "back_main":
                engine.state = "menu"
                menu.reset_cooldown()

            menu.draw(screen, "REALLY QUIT?", menu.confirm_menu)

        # --- PLAYING STATE ---
        elif current_state == "playing":
            engine.update(hand_data, dt)
            renderer.draw_game(engine)

            # Visual feedback for the Pause gesture
            pause_progress = hand_data.get("pause_progress", 0)
            if 0 < pause_progress < 1.0:
                cx = GAME_AREA_X + GAME_AREA_WIDTH // 2
                cy = GAME_AREA_Y + GAME_AREA_HEIGHT // 2

                pygame.draw.circle(screen, (50, 50, 50), (cx, cy), 60, 5)

                # Draw a cyan arc representing the hold time
                pygame.draw.arc(
                    screen,
                    (0, 255, 255),
                    (cx - 60, cy - 60, 120, 120),
                    0,
                    6.28 * pause_progress,
                    5,
                )

        # --- PAUSED STATE ---
        elif current_state == "paused":
            # Handle pause menu navigation with hold gestures
            action = menu.update(
                menu.pause_menu,
                hand_data.get("gesture"),
                dt,
                hold_time=PAUSE_SELECTION_TIME,
            )

            if action == "resume":
                engine.state = "playing"
                menu.reset_cooldown()
            elif action == "restart":
                engine.start_game(engine.game_mode)
                menu.reset_cooldown()
            elif action == "quit_main":
                engine.state = "menu"
                menu.reset_cooldown()

            # Render the game in background and overlay the menu
            renderer.draw_game(engine)
            menu.draw(screen, "PAUSED", menu.pause_menu, overlay=True)

        # --- GAME OVER STATE ---
        elif current_state == "game_over":
            renderer.draw_game(engine)

            # Check for "5" gesture (Open Hand) to return to menu
            if hand_data.get("gesture") == "5":
                engine.state = "menu"
                menu.reset_cooldown()

        # 3. Draw Camera PIP (Picture-in-Picture)
        # This overlays the camera feed on the right corner
        if ret:
            draw_camera_pip(screen, frame, input_ctrl)

        pygame.display.flip()

    # Cleanup resources
    cap.release()
    pygame.quit()
    sys.exit()


def main():
    """Parse arguments and launch the appropriate mode."""
    setup_logging()

    parser = argparse.ArgumentParser(description="AI Pong Game & Analysis Tool")

    # Define the two main operation modes
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--play", action="store_true", help="Launch the main game with UI."
    )

    group.add_argument(
        "--record_data",
        action="store_true",
        help="Launch the data recorder for latency and filter analysis.",
    )

    # Parse arguments
    # If no arguments are passed, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.play:
        run_game_loop()
    elif args.record_data:
        logging.info("Switching to Data Recorder mode.")
        recorder = DataRecorder()
        recorder.run()


if __name__ == "__main__":
    main()

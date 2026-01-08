"""
config.py

Global configuration constants and tuning parameters.
Centralized settings for window layout, gameplay physics, and input mapping.
"""

# --- Display & Layout ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60
GAME_TITLE = "HAND PONG"

# Split Screen Architecture
GAME_AREA_WIDTH = 1200
GAME_AREA_HEIGHT = 900
GAME_AREA_X = 50
GAME_AREA_Y = (WINDOW_HEIGHT - GAME_AREA_HEIGHT) // 2

# Camera PIP Settings
CAMERA_WIDTH = 600
CAMERA_HEIGHT = 450
CAMERA_X = 1280 + (640 - CAMERA_WIDTH) // 2
CAMERA_Y = (WINDOW_HEIGHT - CAMERA_HEIGHT) // 2
CAMERA_BORDER_WIDTH = 4

# --- Hand Tracking Configuration ---
# Which landmark should act as the "Tip" of the lever?
# 4 = Thumb Tip
TRACKING_TARGET_POINT = 4

# Which landmark acts as the "Pivot/Anchor"?
# (5, 6) = Midpoint between Index Knuckle and Middle Joint
# e.g., to use Wrist as anchor, set to 0
TRACKING_ANCHOR_POINT = (5, 6)

# Input Mapping (Angle to Paddle Y)
PADDLE_ANGLE_UP = 100.0
PADDLE_ANGLE_DOWN = 250.0

# Hand Settings
DOMINANT_HAND = "Right"  # "Left" or "Right"
PAUSE_TOGGLE_ENABLED = True
PAUSE_ACTIVATION_TIME = 1.5
PAUSE_SELECTION_TIME = 2.0

# --- Menu Settings ---
MENU_TRANSITION_DELAY = 0.2  # Seconds between menu inputs
MENU_HOLD_TIME = 1.5  # Seconds to hold a gesture to select

# --- Colors (R, G, B) ---
COLOR_BG = (5, 5, 10)
COLOR_GRID = (20, 30, 40)
COLOR_UI_TEXT = (255, 255, 255)
COLOR_UI_GHOST = (200, 200, 200)
COLOR_P1 = (0, 255, 255)  # Cyan (Player 1)
COLOR_P2 = (255, 0, 255)  # Magenta (Bot/P2)
COLOR_TRACKING_GOOD = (0, 255, 0)
COLOR_TRACKING_BAD = (255, 0, 0)
COLOR_WARNING = (255, 200, 0)

# Reusable UI Colors
COLOR_ACCENT_1 = (100, 200, 255)
COLOR_TEXT_DIM = (150, 150, 150)
COLOR_SUCCESS = (50, 200, 50)
COLOR_DANGER = (200, 50, 50)

# --- Gameplay Physics ---
PADDLE_WIDTH = 25
PADDLE_HEIGHT = 140
BALL_RADIUS = 12
KEYBOARD_SPEED = 1000

# Difficulty & Progression
WIN_SCORE = 5
BALL_START_SPEED = 15
BALL_MAX_SPEED = 25
SPEED_INCREMENT_PER_HIT = 0.5
HITS_PER_LEVEL = 5
SPEED_INCREMENT_PER_LEVEL = 2.0
TIME_LIMIT = 120

# Math Task Settings
MATH_TASK_DURATION = 10.0
MATH_TASK_INTERVAL = 25.0

# Powerups
POWERUP_DURATION = 15.0
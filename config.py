# --- DISPLAY ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# --- LAYOUT ---
GAME_AREA_WIDTH = 1200
GAME_AREA_HEIGHT = 900
GAME_AREA_X = 80
GAME_AREA_Y = 90

CAMERA_WIDTH = 500
CAMERA_HEIGHT = 650
CAMERA_X = GAME_AREA_X + GAME_AREA_WIDTH + 30
CAMERA_Y = (WINDOW_HEIGHT - CAMERA_HEIGHT) // 2
CAMERA_BORDER_WIDTH = 4

# --- COLORS (Neon / Cyberpunk Theme) ---
COLOR_BG = (10, 10, 16)           # Deep dark blue/black
COLOR_UI_BG = (20, 24, 35)         # Slightly lighter for UI panels
COLOR_ACCENT_1 = (0, 255, 200)     # Cyan (Player / Highlight)
COLOR_ACCENT_2 = (255, 0, 128)     # Magenta (AI / Enemy)
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (120, 130, 140)
COLOR_WARNING = (255, 165, 0)      # Orange for warnings/confirmations
COLOR_SUCCESS = (50, 255, 50)      # Green
COLOR_GLOW = (255, 255, 255)       # White glow core


CONFIRM_HOLD_TIME = 1
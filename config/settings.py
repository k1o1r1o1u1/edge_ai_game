# config/settings.py

# Game Setup
FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Serial Configuration (Sensible defaults)
# Users can modify this file if their setup differs.
SERIAL_PORT = "AUTO"  # Set to "AUTO" to auto-detect ESP32, or a specific port like "COM3"
BAUD_RATE = 115200

# Colors (Simple and Polished - not overly vibrant)
COLOR_BG = (30, 30, 30)          # Dark grey background
COLOR_TEXT = (220, 220, 220)     # Off-white for text
COLOR_PLAYER = (60, 140, 200)    # Muted Blue
COLOR_BOSS = (200, 60, 60)       # Muted Red
COLOR_HEALTH_BG = (50, 50, 50)
COLOR_HEALTH_FG = (60, 180, 80)
COLOR_HEALTH_BOSS = (180, 60, 60)

COLOR_BLOCK = (200, 180, 60)     # Muted Gold/Yellow
COLOR_DODGE = (60, 200, 180)     # Muted Cyan
COLOR_SPECIAL = (160, 60, 200)   # Muted Purple
COLOR_HIT = (255, 255, 255)      # White flash

# Combat Mechanics
PLAYER_MAX_HP = 100
BOSS_MAX_HP = 500

# Damage values
DMG_PUNCH = 10
DMG_SPECIAL = 50
DMG_BOSS_ATTACK = 15

# Cooldowns (milliseconds)
# This prevents one physical gesture from spamming actions
COOLDOWN_ACTION = 500      # 0.5s between player actions minimum
COOLDOWN_BOSS_ATTACK = 2000 # Boss attacks every 2 seconds roughly

# Durations (milliseconds)
DURATION_BLOCK = 1000      # Block lasts for 1 second
DURATION_DODGE = 800       # Dodge lasts for 0.8 seconds
DURATION_HIT_FLASH = 150   # How long hit flash stays on screen

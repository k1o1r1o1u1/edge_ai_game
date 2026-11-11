# config/settings.py

# Game Setup
FPS = 60
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600

# Serial Configuration (Sensible defaults)
SERIAL_PORT = "AUTO"  # Set to "AUTO" to auto-detect ESP32, or a specific port like "COM3"
BAUD_RATE = 115200

# Colors & Theme (Modern Arcade / Cyber Fighter)
COLOR_BG_DARK = (15, 17, 26)
COLOR_BG_GRADIENT = (25, 30, 48)
COLOR_ARENA_FLOOR = (28, 32, 50)
COLOR_ARENA_LINE = (0, 230, 255)

COLOR_TEXT = (240, 245, 255)
COLOR_TEXT_DIM = (140, 150, 175)
COLOR_ACCENT = (0, 220, 255)

COLOR_PLAYER = (50, 160, 255)
COLOR_PLAYER_GLOW = (0, 190, 255)
COLOR_BOSS = (255, 60, 90)
COLOR_BOSS_GLOW = (255, 30, 70)

COLOR_HEALTH_BG = (35, 40, 55)
COLOR_HEALTH_BORDER = (80, 90, 120)
COLOR_HEALTH_PLAYER = (0, 230, 130)
COLOR_HEALTH_BOSS = (255, 60, 80)
COLOR_HEALTH_DAMAGE_LAG = (235, 175, 40)

# Charge Meter Colors
COLOR_SPECIAL_BAR_BG = (25, 25, 40)
COLOR_SPECIAL_CHARGE_LOW = (140, 60, 240)
COLOR_SPECIAL_CHARGE_FULL = (255, 215, 0)
COLOR_SPECIAL_GLOW = (255, 230, 80)

# State Colors & Effects
COLOR_BLOCK = (255, 200, 50)
COLOR_DODGE = (50, 240, 220)
COLOR_SPECIAL = (180, 70, 255)
COLOR_HIT = (255, 255, 255)

# Combat Mechanics
PLAYER_MAX_HP = 100

# Charge System Mechanics
# Special starts at 0%, requires FULL 100% to unleash!
SPECIAL_MAX_CHARGE = 100
SPECIAL_MIN_REQUIRED = 100       # Full 100% required!
CHARGE_PER_PUNCH = 15            # Granted when punch connects with boss
CHARGE_PER_PERFECT_BLOCK = 20    # Granted on successful shield absorption of boss attack
CHARGE_PER_DODGE = 25            # Granted on successful evasion of boss attack
CHARGE_PASSIVE_RATE = 0.0        # No passive increase when idle

# Player Damage values
DMG_PUNCH = 14
DMG_SPECIAL = 120                # Massive catastrophic damage at 100% full charge

# Difficulty Presets (EASY, MEDIUM, HARD)
DIFFICULTY_SETTINGS = {
    "EASY": {
        "boss_max_hp": 300,           # Low HP: easy to defeat!
        "boss_dmg_normal": 5,         # Very gentle boss attacks
        "boss_dmg_heavy": 10,
        "cooldown_boss_attack": 3600, # Very slow, predictable attacks (3.6s)
        "prep_normal_ms": 1500,       # 1.5s reaction warning
        "prep_heavy_ms": 1900,
        "heavy_chance": 0.10,
        "boss_block_chance": 0.05,    # Barely blocks (5%)
        "boss_dodge_chance": 0.02,    # Almost never dodges (2%)
        "color": (50, 230, 140)       # Green
    },
    "MEDIUM": {
        "boss_max_hp": 550,           # Balanced HP
        "boss_dmg_normal": 10,        # Balanced damage
        "boss_dmg_heavy": 18,
        "cooldown_boss_attack": 2300, # 2.3s attack pace
        "prep_normal_ms": 950,
        "prep_heavy_ms": 1250,
        "heavy_chance": 0.30,
        "boss_block_chance": 0.22,    # Blocks 22% of incoming player attacks
        "boss_dodge_chance": 0.15,    # Dodges 15% of incoming player attacks
        "color": (255, 200, 50)       # Yellow
    },
    "HARD": {
        "boss_max_hp": 850,           # High durability: true endurance fight!
        "boss_dmg_normal": 22,        # Punishing, deadly attacks
        "boss_dmg_heavy": 40,
        "cooldown_boss_attack": 1400, # Relentless, rapid aggression (1.4s)
        "prep_normal_ms": 600,        # Fast 0.6s reflex test
        "prep_heavy_ms": 800,
        "heavy_chance": 0.50,         # 50% chance of heavy attack
        "boss_block_chance": 0.38,    # Frequently blocks (38%)
        "boss_dodge_chance": 0.28,    # Smart evasive jumps (28%)
        "color": (255, 60, 80)        # Red
    }
}

DEFAULT_DIFFICULTY = "MEDIUM"

# Cooldowns (milliseconds)
COOLDOWN_ACTION = 380

# Durations (milliseconds)
DURATION_BLOCK = 1500      # 1.5 seconds shield duration
DURATION_DODGE = 900
DURATION_HIT_FLASH = 140

# Projectile Mechanics
PROJECTILE_SPEED_PUNCH = 24
PROJECTILE_SPEED_SPECIAL = 18

# Audio Settings
DEFAULT_SFX_VOLUME = 0.8
DEFAULT_BGM_VOLUME = 0.4
